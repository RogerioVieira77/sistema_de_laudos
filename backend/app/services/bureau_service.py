"""
Bureau Service - Business logic for bureau data
"""

from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import datetime

from app.repositories import BureauRepository, ContratoRepository, LogsAnaliseRepository
from app.models.dados_bureau import DadosBureau
from app.schemas import DadosBureauCreate, DadosBureauResponse, DadosBureauListResponse
from app.utils import NominatimClient
from .base_service import BaseService


class BureauService(BaseService):
    """Service for bureau data operations"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.bureau_repo = BureauRepository(db)
        self.contrato_repo = ContratoRepository(db)
        self.logs_repo = LogsAnaliseRepository(db)
        self.nominatim = NominatimClient()

    def criar_bureau_data(
        self,
        bureau_data: DadosBureauCreate,
        usuario_id: int
    ) -> DadosBureauResponse:
        """
        Create bureau data record.

        Args:
            bureau_data: Bureau data
            usuario_id: User ID

        Returns:
            Created bureau data response
        """
        try:
            # Verify contract exists
            contrato = self.contrato_repo.get_by_id(bureau_data.contrato_id)
            if not contrato:
                raise ValueError(f"Contract {bureau_data.contrato_id} not found")

            # Create bureau record
            bureau = self.bureau_repo.create(bureau_data.dict())

            # Log creation
            self.logs_repo.create({
                "contrato_id": bureau_data.contrato_id,
                "usuario_id": usuario_id,
                "tipo_evento": "PROCESSANDO",
                "mensagem": f"Dados de bureau carregados para cliente {bureau_data.nome_cliente}",
            })

            self.log_info(f"Created bureau data {bureau.id} for contract {bureau_data.contrato_id}")

            return DadosBureauResponse.from_orm(bureau)

        except Exception as e:
            self.log_error(f"Error creating bureau data", e)
            raise

    def obter_bureau_data(self, bureau_id: int) -> Optional[DadosBureauResponse]:
        """
        Get bureau data by ID.

        Args:
            bureau_id: Bureau data ID

        Returns:
            Bureau data response or None
        """
        bureau = self.bureau_repo.get_by_id(bureau_id)
        if bureau:
            return DadosBureauResponse.from_orm(bureau)
        return None

    def obter_por_contrato(self, contrato_id: int) -> Optional[DadosBureauResponse]:
        """
        Get bureau data by contract.

        Args:
            contrato_id: Contract ID

        Returns:
            Bureau data response or None
        """
        bureau = self.bureau_repo.get_by_contrato(contrato_id)
        if bureau:
            return DadosBureauResponse.from_orm(bureau)
        return None

    def buscar_por_cpf(self, cpf: str) -> DadosBureauListResponse:
        """
        Search bureau data by CPF.

        Args:
            cpf: Customer CPF

        Returns:
            List of bureau data
        """
        bureaus = self.bureau_repo.get_by_cpf(cpf)
        return DadosBureauListResponse(
            total=len(bureaus),
            dados=[DadosBureauResponse.from_orm(b) for b in bureaus]
        )

    def buscar_por_nome(
        self,
        nome: str,
        skip: int = 0,
        limit: int = 10
    ) -> DadosBureauListResponse:
        """
        Search bureau data by customer name.

        Args:
            nome: Customer name
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            List of bureau data
        """
        bureaus, total = self.bureau_repo.search_by_nome(nome, skip, limit)
        return DadosBureauListResponse(
            total=total,
            dados=[DadosBureauResponse.from_orm(b) for b in bureaus]
        )

    def geocodificar_endereco_bureau(
        self,
        bureau_id: int,
        usuario_id: int
    ) -> Optional[DadosBureauResponse]:
        """
        Geocode bureau address and update coordinates.

        Args:
            bureau_id: Bureau data ID
            usuario_id: User ID

        Returns:
            Updated bureau data or None
        """
        try:
            bureau = self.bureau_repo.get_by_id(bureau_id)
            if not bureau:
                raise ValueError(f"Bureau data {bureau_id} not found")

            # Geocode address
            result = self.nominatim.geocode_sync(bureau.logradouro)
            if result:
                lat, lon, formatted_address = result

                # Update location
                updated = self.bureau_repo.update_location(
                    bureau_id,
                    lat,
                    lon,
                    datetime.utcnow()
                )

                self.log_info(f"Geocoded bureau {bureau_id}: {lat}, {lon}")

                return DadosBureauResponse.from_orm(updated)
            else:
                raise ValueError(f"Could not geocode address: {bureau.logradouro}")

        except Exception as e:
            self.log_error(f"Error geocoding bureau address {bureau_id}", e)
            raise

    def obter_sem_localizacao(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> DadosBureauListResponse:
        """
        Get bureau records without geocoded location.

        Args:
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            List of bureau data without location
        """
        bureaus, total = self.bureau_repo.get_without_location(skip, limit)
        return DadosBureauListResponse(
            total=total,
            dados=[DadosBureauResponse.from_orm(b) for b in bureaus]
        )

    def get_estatisticas_bureau(self) -> dict:
        """
        Get bureau statistics.

        Returns:
            Statistics dictionary
        """
        total = self.bureau_repo.count()
        geocoded = self.bureau_repo.get_geocoded_count()
        not_geocoded = total - geocoded

        return {
            "total": total,
            "geocodificados": geocoded,
            "sem_geocodificacao": not_geocoded,
            "percentual_geocodificacao": (geocoded / total * 100) if total > 0 else 0,
        }

    def deletar_bureau_data(self, bureau_id: int) -> bool:
        """
        Delete bureau data.

        Args:
            bureau_id: Bureau data ID

        Returns:
            True if deleted, False otherwise
        """
        return self.bureau_repo.delete(bureau_id)

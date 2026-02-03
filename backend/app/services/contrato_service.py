"""
Contrato Service - Business logic for contracts
"""

from sqlalchemy.orm import Session
from typing import Optional, Tuple, List
from datetime import datetime

from app.repositories import ContratoRepository, UsuarioRepository, LogsAnaliseRepository
from app.models.dados_contrato import DadosContrato
from app.schemas import DadosContratoCreate, DadosContratoResponse, DadosContratoListResponse
from .base_service import BaseService


class ContratoService(BaseService):
    """Service for contract operations"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.contrato_repo = ContratoRepository(db)
        self.usuario_repo = UsuarioRepository(db)
        self.logs_repo = LogsAnaliseRepository(db)

    def create_contrato(
        self,
        contrato_data: DadosContratoCreate
    ) -> DadosContratoResponse:
        """
        Create a new contract with validation.

        Args:
            contrato_data: Contract data

        Returns:
            Created contract response
        """
        try:
            # Verify user exists
            usuario = self.usuario_repo.get_by_id(contrato_data.usuario_id)
            if not usuario:
                raise ValueError(f"Usuario {contrato_data.usuario_id} not found")

            # Check if contract already exists
            existing = self.contrato_repo.get_by_cpf_and_numero(
                contrato_data.cpf_cliente,
                contrato_data.numero_contrato
            )
            if existing:
                raise ValueError("Contract already exists for this CPF and number")

            # Create contract
            contrato = self.contrato_repo.create(contrato_data.dict())

            # Log creation
            self.logs_repo.create({
                "contrato_id": contrato.id,
                "usuario_id": contrato_data.usuario_id,
                "tipo_evento": "UPLOAD",
                "mensagem": f"Contrato {contrato_data.numero_contrato} carregado com sucesso",
            })

            self.log_info(f"Created contract {contrato.id} for user {contrato_data.usuario_id}")

            return DadosContratoResponse.from_orm(contrato)

        except Exception as e:
            self.log_error(f"Error creating contract", e)
            raise

    def get_contrato(self, contrato_id: int) -> Optional[DadosContratoResponse]:
        """
        Get contract by ID.

        Args:
            contrato_id: Contract ID

        Returns:
            Contract response or None
        """
        contrato = self.contrato_repo.get_by_id(contrato_id)
        if contrato:
            return DadosContratoResponse.from_orm(contrato)
        return None

    def get_contratos_usuario(
        self,
        usuario_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> DadosContratoListResponse:
        """
        Get all contracts for a user.

        Args:
            usuario_id: User ID
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            List of contracts with pagination
        """
        contratos, total = self.contrato_repo.get_by_usuario(usuario_id, skip, limit)
        return DadosContratoListResponse(
            total=total,
            page=skip // limit + 1,
            limit=limit,
            contratos=[DadosContratoResponse.from_orm(c) for c in contratos]
        )

    def search_contratos(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 10
    ) -> DadosContratoListResponse:
        """
        Search contracts by CPF or number.

        Args:
            search_term: Search string
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            List of matching contracts
        """
        contratos, total = self.contrato_repo.search(search_term, skip, limit)
        return DadosContratoListResponse(
            total=total,
            page=skip // limit + 1,
            limit=limit,
            contratos=[DadosContratoResponse.from_orm(c) for c in contratos]
        )

    def get_contratos_por_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 10
    ) -> DadosContratoListResponse:
        """
        Get contracts by status.

        Args:
            status: Contract status
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            List of contracts with pagination
        """
        contratos, total = self.contrato_repo.get_by_status(status, skip, limit)
        return DadosContratoListResponse(
            total=total,
            page=skip // limit + 1,
            limit=limit,
            contratos=[DadosContratoResponse.from_orm(c) for c in contratos]
        )

    def atualizar_status(
        self,
        contrato_id: int,
        novo_status: str,
        usuario_id: int
    ) -> Optional[DadosContratoResponse]:
        """
        Update contract status.

        Args:
            contrato_id: Contract ID
            novo_status: New status
            usuario_id: User ID making the change

        Returns:
            Updated contract or None
        """
        contrato = self.contrato_repo.update_status(contrato_id, novo_status)
        if contrato:
            self.logs_repo.create({
                "contrato_id": contrato_id,
                "usuario_id": usuario_id,
                "tipo_evento": "PROCESSANDO" if novo_status == "PROCESSANDO" else "SUCESSO",
                "mensagem": f"Status atualizado para {novo_status}",
            })
            return DadosContratoResponse.from_orm(contrato)
        return None

    def atualizar_localizacao(
        self,
        contrato_id: int,
        latitude,
        longitude
    ) -> Optional[DadosContratoResponse]:
        """
        Update contract location.

        Args:
            contrato_id: Contract ID
            latitude: Latitude
            longitude: Longitude

        Returns:
            Updated contract or None
        """
        contrato = self.contrato_repo.update_location(contrato_id, latitude, longitude)
        if contrato:
            return DadosContratoResponse.from_orm(contrato)
        return None

    def delete_contrato(self, contrato_id: int) -> bool:
        """
        Delete a contract.

        Args:
            contrato_id: Contract ID

        Returns:
            True if deleted, False otherwise
        """
        return self.contrato_repo.delete(contrato_id)

    def get_contratos_recentes(
        self,
        dias: int = 7,
        skip: int = 0,
        limit: int = 10
    ) -> DadosContratoListResponse:
        """
        Get recent contracts.

        Args:
            dias: Number of days back
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            List of recent contracts
        """
        contratos, total = self.contrato_repo.get_recent(dias, skip, limit)
        return DadosContratoListResponse(
            total=total,
            page=skip // limit + 1,
            limit=limit,
            contratos=[DadosContratoResponse.from_orm(c) for c in contratos]
        )

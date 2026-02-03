"""
Parecer Service - Business logic for parecer (analysis opinion) generation
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from app.repositories import PareceRepository, ContratoRepository, LogsAnaliseRepository
from app.models.parecer import Parecer
from app.schemas import (
    PareceCreate,
    PareceResponse,
    PareceListResponse,
    PareceFilterRequest,
)
from .base_service import BaseService


class PareceService(BaseService):
    """Service for parecer (analysis opinion) generation and management"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.parecer_repo = PareceRepository(db)
        self.contrato_repo = ContratoRepository(db)
        self.logs_repo = LogsAnaliseRepository(db)

    def criar_parecer(
        self,
        parecer_data: PareceCreate,
        usuario_id: int
    ) -> PareceResponse:
        """
        Create a new parecer (analysis opinion).

        Args:
            parecer_data: Parecer data
            usuario_id: User ID

        Returns:
            Created parecer response
        """
        try:
            # Verify contract exists
            contrato = self.contrato_repo.get_by_id(parecer_data.contrato_id)
            if not contrato:
                raise ValueError(f"Contract {parecer_data.contrato_id} not found")

            # Create parecer
            parecer = self.parecer_repo.create(parecer_data.dict())

            # Log creation
            self.logs_repo.create({
                "contrato_id": parecer_data.contrato_id,
                "usuario_id": usuario_id,
                "tipo_evento": "PARECER_GERADO",
                "mensagem": f"Parecer de tipo {parecer_data.tipo} gerado com sucesso",
            })

            self.log_info(f"Created parecer {parecer.id} for contract {parecer_data.contrato_id}")

            return PareceResponse.from_orm(parecer)

        except Exception as e:
            self.log_error(f"Error creating parecer", e)
            raise

    def obter_parecer(self, parecer_id: int) -> Optional[PareceResponse]:
        """
        Get parecer by ID.

        Args:
            parecer_id: Parecer ID

        Returns:
            Parecer response or None
        """
        parecer = self.parecer_repo.get_by_id(parecer_id)
        if parecer:
            return PareceResponse.from_orm(parecer)
        return None

    def obter_pareceres_contrato(
        self,
        contrato_id: int
    ) -> PareceListResponse:
        """
        Get all pareceres for a contract.

        Args:
            contrato_id: Contract ID

        Returns:
            List of pareceres
        """
        pareceres = self.parecer_repo.get_by_contrato(contrato_id)
        return PareceListResponse(
            total=len(pareceres),
            pareceres=[PareceResponse.from_orm(p) for p in pareceres]
        )

    def obter_por_tipo(
        self,
        tipo: str,
        skip: int = 0,
        limit: int = 10
    ) -> PareceListResponse:
        """
        Get pareceres by type.

        Args:
            tipo: Parecer type (PROXIMAL, MODERADO, DISTANTE, MUITO_DISTANTE)
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            List of pareceres
        """
        pareceres, total = self.parecer_repo.get_by_tipo(tipo, skip, limit)
        return PareceListResponse(
            total=total,
            pareceres=[PareceResponse.from_orm(p) for p in pareceres]
        )

    def obter_por_faixa_distancia(
        self,
        distancia_minima: Decimal,
        distancia_maxima: Decimal,
        skip: int = 0,
        limit: int = 10
    ) -> PareceListResponse:
        """
        Get pareceres by distance range.

        Args:
            distancia_minima: Minimum distance in km
            distancia_maxima: Maximum distance in km
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            List of pareceres within distance range
        """
        pareceres, total = self.parecer_repo.get_by_distance_range(
            distancia_minima,
            distancia_maxima,
            skip,
            limit
        )
        return PareceListResponse(
            total=total,
            pareceres=[PareceResponse.from_orm(p) for p in pareceres]
        )

    def filtrar_pareceres(
        self,
        filtro: PareceFilterRequest,
        skip: int = 0,
        limit: int = 10
    ) -> PareceListResponse:
        """
        Filter pareceres with multiple criteria.

        Args:
            filtro: Filter request
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            Filtered pareceres
        """
        pareceres, total = self.parecer_repo.search(
            tipo=filtro.tipo,
            distancia_minima=filtro.distancia_minima,
            distancia_maxima=filtro.distancia_maxima,
            data_inicio=filtro.data_inicio,
            data_fim=filtro.data_fim,
            skip=skip,
            limit=limit
        )
        return PareceListResponse(
            total=total,
            pareceres=[PareceResponse.from_orm(p) for p in pareceres]
        )

    def atualizar_parecer(
        self,
        parecer_id: int,
        parecer_update: dict,
        usuario_id: int
    ) -> Optional[PareceResponse]:
        """
        Update parecer data.

        Args:
            parecer_id: Parecer ID
            parecer_update: Update data
            usuario_id: User ID

        Returns:
            Updated parecer or None
        """
        try:
            parecer = self.parecer_repo.update(parecer_id, parecer_update)
            if parecer:
                self.logs_repo.create({
                    "contrato_id": parecer.contrato_id,
                    "usuario_id": usuario_id,
                    "tipo_evento": "PARECER_ATUALIZADO",
                    "mensagem": f"Parecer {parecer_id} atualizado",
                })
                self.log_info(f"Updated parecer {parecer_id}")
                return PareceResponse.from_orm(parecer)
            return None

        except Exception as e:
            self.log_error(f"Error updating parecer {parecer_id}", e)
            raise

    def get_estatisticas_pareceres(self) -> dict:
        """
        Get parecer statistics.

        Returns:
            Statistics dictionary with counts by type
        """
        stats = self.parecer_repo.get_statistics()
        total = sum(v for k, v in stats.items() if k != "total")

        return {
            "total": total,
            "por_tipo": {
                "proximal": stats.get("PROXIMAL", 0),
                "moderado": stats.get("MODERADO", 0),
                "distante": stats.get("DISTANTE", 0),
                "muito_distante": stats.get("MUITO_DISTANTE", 0),
            },
            "percentual_por_tipo": {
                "proximal": (stats.get("PROXIMAL", 0) / total * 100) if total > 0 else 0,
                "moderado": (stats.get("MODERADO", 0) / total * 100) if total > 0 else 0,
                "distante": (stats.get("DISTANTE", 0) / total * 100) if total > 0 else 0,
                "muito_distante": (stats.get("MUITO_DISTANTE", 0) / total * 100) if total > 0 else 0,
            },
        }

    def contar_por_tipo(self, tipo: str) -> int:
        """
        Count pareceres by type.

        Args:
            tipo: Parecer type

        Returns:
            Count of pareceres
        """
        return self.parecer_repo.count_by_tipo(tipo)

    def deletar_parecer(self, parecer_id: int) -> bool:
        """
        Delete parecer.

        Args:
            parecer_id: Parecer ID

        Returns:
            True if deleted, False otherwise
        """
        return self.parecer_repo.delete(parecer_id)

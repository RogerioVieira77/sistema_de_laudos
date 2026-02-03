"""
DadosContrato Repository - Data Access Layer for DadosContrato model
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.dados_contrato import DadosContrato
from .base_repository import BaseRepository


class ContratoRepository(BaseRepository[DadosContrato]):
    """Repository for DadosContrato model"""

    def __init__(self, db: Session):
        super().__init__(db, DadosContrato)

    def get_by_cpf(self, cpf: str) -> Optional[DadosContrato]:
        """
        Get contract by CPF.

        Args:
            cpf: Customer CPF

        Returns:
            DadosContrato object or None
        """
        return self.db.query(DadosContrato).filter(
            DadosContrato.cpf_cliente == cpf
        ).first()

    def get_by_numero_contrato(self, numero: str) -> Optional[DadosContrato]:
        """
        Get contract by contract number.

        Args:
            numero: Contract number

        Returns:
            DadosContrato object or None
        """
        return self.db.query(DadosContrato).filter(
            DadosContrato.numero_contrato == numero
        ).first()

    def get_by_usuario(
        self,
        usuario_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[DadosContrato], int]:
        """
        Get contracts by user.

        Args:
            usuario_id: User ID
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (contracts list, total count)
        """
        query = self.db.query(DadosContrato).filter(
            DadosContrato.usuario_id == usuario_id
        )
        total = query.count()
        contracts = query.offset(skip).limit(limit).all()
        return contracts, total

    def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[DadosContrato], int]:
        """
        Get contracts by status.

        Args:
            status: Contract status
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (contracts list, total count)
        """
        query = self.db.query(DadosContrato).filter(
            DadosContrato.status == status
        )
        total = query.count()
        contracts = query.offset(skip).limit(limit).all()
        return contracts, total

    def get_recent(
        self,
        days: int = 7,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[DadosContrato], int]:
        """
        Get contracts from the last N days.

        Args:
            days: Number of days back
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (contracts list, total count)
        """
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(DadosContrato).filter(
            DadosContrato.criado_em >= start_date
        )
        total = query.count()
        contracts = query.offset(skip).limit(limit).all()
        return contracts, total

    def get_by_cpf_and_numero(
        self,
        cpf: str,
        numero: str
    ) -> Optional[DadosContrato]:
        """
        Get contract by CPF and contract number.

        Args:
            cpf: Customer CPF
            numero: Contract number

        Returns:
            DadosContrato object or None
        """
        return self.db.query(DadosContrato).filter(
            and_(
                DadosContrato.cpf_cliente == cpf,
                DadosContrato.numero_contrato == numero
            )
        ).first()

    def search(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[DadosContrato], int]:
        """
        Search contracts by CPF or contract number.

        Args:
            search_term: Search string
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (contracts list, total count)
        """
        query = self.db.query(DadosContrato).filter(
            or_(
                DadosContrato.cpf_cliente.like(f"%{search_term}%"),
                DadosContrato.numero_contrato.like(f"%{search_term}%")
            )
        )
        total = query.count()
        contracts = query.offset(skip).limit(limit).all()
        return contracts, total

    def update_status(
        self,
        contrato_id: int,
        new_status: str
    ) -> Optional[DadosContrato]:
        """
        Update contract status.

        Args:
            contrato_id: Contract ID
            new_status: New status value

        Returns:
            Updated contract or None
        """
        return self.update(contrato_id, {"status": new_status})

    def update_location(
        self,
        contrato_id: int,
        latitude,
        longitude
    ) -> Optional[DadosContrato]:
        """
        Update contract location coordinates.

        Args:
            contrato_id: Contract ID
            latitude: Latitude
            longitude: Longitude

        Returns:
            Updated contract or None
        """
        return self.update(
            contrato_id,
            {"latitude": latitude, "longitude": longitude}
        )

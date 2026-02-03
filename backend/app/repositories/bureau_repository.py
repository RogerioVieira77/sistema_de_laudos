"""
DadosBureau Repository - Data Access Layer for DadosBureau model
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.dados_bureau import DadosBureau
from .base_repository import BaseRepository


class BureauRepository(BaseRepository[DadosBureau]):
    """Repository for DadosBureau model"""

    def __init__(self, db: Session):
        super().__init__(db, DadosBureau)

    def get_by_contrato(self, contrato_id: int) -> Optional[DadosBureau]:
        """
        Get bureau data by contract ID.

        Args:
            contrato_id: Contract ID

        Returns:
            DadosBureau object or None
        """
        return self.db.query(DadosBureau).filter(
            DadosBureau.contrato_id == contrato_id
        ).first()

    def get_by_cpf(self, cpf: str) -> List[DadosBureau]:
        """
        Get all bureau records by CPF.

        Args:
            cpf: Customer CPF

        Returns:
            List of DadosBureau objects
        """
        return self.db.query(DadosBureau).filter(
            DadosBureau.cpf_cliente == cpf
        ).all()

    def get_by_cep(
        self,
        cep: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[DadosBureau], int]:
        """
        Get bureau records by CEP.

        Args:
            cep: CEP code
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (records list, total count)
        """
        query = self.db.query(DadosBureau).filter(DadosBureau.cep == cep)
        total = query.count()
        records = query.offset(skip).limit(limit).all()
        return records, total

    def get_without_location(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[DadosBureau], int]:
        """
        Get bureau records without geocoded location.

        Args:
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (records list, total count)
        """
        query = self.db.query(DadosBureau).filter(
            (DadosBureau.latitude.is_(None)) | (DadosBureau.longitude.is_(None))
        )
        total = query.count()
        records = query.offset(skip).limit(limit).all()
        return records, total

    def get_recent(
        self,
        days: int = 7,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[DadosBureau], int]:
        """
        Get bureau records from the last N days.

        Args:
            days: Number of days back
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (records list, total count)
        """
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(DadosBureau).filter(
            DadosBureau.criado_em >= start_date
        )
        total = query.count()
        records = query.offset(skip).limit(limit).all()
        return records, total

    def update_location(
        self,
        bureau_id: int,
        latitude,
        longitude,
        data_consulta: Optional[datetime] = None
    ) -> Optional[DadosBureau]:
        """
        Update bureau location coordinates.

        Args:
            bureau_id: Bureau record ID
            latitude: Latitude
            longitude: Longitude
            data_consulta: Query date

        Returns:
            Updated record or None
        """
        update_data = {
            "latitude": latitude,
            "longitude": longitude
        }
        if data_consulta:
            update_data["data_consulta"] = data_consulta
        
        return self.update(bureau_id, update_data)

    def get_geocoded_count(self) -> int:
        """
        Count bureau records with geocoded location.

        Returns:
            Count of geocoded records
        """
        return self.db.query(DadosBureau).filter(
            (DadosBureau.latitude.isnot(None)) &
            (DadosBureau.longitude.isnot(None))
        ).count()

    def search_by_nome(
        self,
        nome: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[DadosBureau], int]:
        """
        Search bureau records by customer name.

        Args:
            nome: Customer name
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (records list, total count)
        """
        query = self.db.query(DadosBureau).filter(
            DadosBureau.nome_cliente.ilike(f"%{nome}%")
        )
        total = query.count()
        records = query.offset(skip).limit(limit).all()
        return records, total

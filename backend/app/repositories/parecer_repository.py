"""
Parecer Repository - Data Access Layer for Parecer model
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from decimal import Decimal

from app.models.parecer import Parecer
from .base_repository import BaseRepository


class PareceRepository(BaseRepository[Parecer]):
    """Repository for Parecer model"""

    def __init__(self, db: Session):
        super().__init__(db, Parecer)

    def get_by_contrato(self, contrato_id: int) -> Optional[Parecer]:
        """
        Get parecer by contract ID (one-to-one relationship).

        Args:
            contrato_id: Contract ID

        Returns:
            Parecer object or None
        """
        return self.db.query(Parecer).filter(
            Parecer.contrato_id == contrato_id
        ).first()

    def get_by_tipo(
        self,
        tipo_parecer: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Parecer], int]:
        """
        Get pareceres by type.

        Args:
            tipo_parecer: Type (PROXIMAL, MODERADO, DISTANTE, MUITO_DISTANTE)
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (pareceres list, total count)
        """
        query = self.db.query(Parecer).filter(
            Parecer.tipo_parecer == tipo_parecer
        ).order_by(desc(Parecer.criado_em))
        total = query.count()
        pareceres = query.offset(skip).limit(limit).all()
        return pareceres, total

    def get_by_distance_range(
        self,
        min_distance: Decimal,
        max_distance: Decimal,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Parecer], int]:
        """
        Get pareceres within distance range.

        Args:
            min_distance: Minimum distance in km
            max_distance: Maximum distance in km
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (pareceres list, total count)
        """
        query = self.db.query(Parecer).filter(
            and_(
                Parecer.distancia_km >= min_distance,
                Parecer.distancia_km <= max_distance
            )
        ).order_by(Parecer.distancia_km)
        total = query.count()
        pareceres = query.offset(skip).limit(limit).all()
        return pareceres, total

    def get_recent(
        self,
        days: int = 7,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Parecer], int]:
        """
        Get pareceres from the last N days.

        Args:
            days: Number of days back
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (pareceres list, total count)
        """
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(Parecer).filter(
            Parecer.criado_em >= start_date
        ).order_by(desc(Parecer.criado_em))
        total = query.count()
        pareceres = query.offset(skip).limit(limit).all()
        return pareceres, total

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Parecer], int]:
        """
        Get pareceres within date range.

        Args:
            start_date: Start date
            end_date: End date
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (pareceres list, total count)
        """
        query = self.db.query(Parecer).filter(
            and_(
                Parecer.criado_em >= start_date,
                Parecer.criado_em <= end_date
            )
        ).order_by(desc(Parecer.criado_em))
        total = query.count()
        pareceres = query.offset(skip).limit(limit).all()
        return pareceres, total

    def get_by_tipo_and_date(
        self,
        tipo_parecer: str,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Parecer], int]:
        """
        Get pareceres by type and date range.

        Args:
            tipo_parecer: Parecer type
            start_date: Start date
            end_date: End date
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (pareceres list, total count)
        """
        query = self.db.query(Parecer).filter(
            and_(
                Parecer.tipo_parecer == tipo_parecer,
                Parecer.criado_em >= start_date,
                Parecer.criado_em <= end_date
            )
        ).order_by(desc(Parecer.criado_em))
        total = query.count()
        pareceres = query.offset(skip).limit(limit).all()
        return pareceres, total

    def get_average_distance_by_tipo(self, tipo_parecer: str) -> Optional[Decimal]:
        """
        Get average distance for a parecer type.

        Args:
            tipo_parecer: Parecer type

        Returns:
            Average distance or None
        """
        from sqlalchemy import func
        result = self.db.query(
            func.avg(Parecer.distancia_km)
        ).filter(
            Parecer.tipo_parecer == tipo_parecer
        ).scalar()
        return result

    def count_by_tipo(self, tipo_parecer: str) -> int:
        """
        Count pareceres by type.

        Args:
            tipo_parecer: Parecer type

        Returns:
            Count
        """
        return self.db.query(Parecer).filter(
            Parecer.tipo_parecer == tipo_parecer
        ).count()

    def get_statistics(self) -> dict:
        """
        Get statistics about all pareceres.

        Returns:
            Dictionary with statistics
        """
        from sqlalchemy import func
        
        total = self.count()
        
        type_counts = self.db.query(
            Parecer.tipo_parecer,
            func.count(Parecer.id)
        ).group_by(Parecer.tipo_parecer).all()
        
        avg_distance = self.db.query(
            func.avg(Parecer.distancia_km)
        ).scalar()
        
        max_distance = self.db.query(
            func.max(Parecer.distancia_km)
        ).scalar()
        
        min_distance = self.db.query(
            func.min(Parecer.distancia_km)
        ).scalar()
        
        return {
            "total": total,
            "by_tipo": {tipo: count for tipo, count in type_counts},
            "avg_distance": float(avg_distance) if avg_distance else None,
            "max_distance": float(max_distance) if max_distance else None,
            "min_distance": float(min_distance) if min_distance else None,
        }

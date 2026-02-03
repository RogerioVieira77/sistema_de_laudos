"""
LogsAnalise Repository - Data Access Layer for LogsAnalise model
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.logs_analise import LogsAnalise
from .base_repository import BaseRepository


class LogsAnaliseRepository(BaseRepository[LogsAnalise]):
    """Repository for LogsAnalise model"""

    def __init__(self, db: Session):
        super().__init__(db, LogsAnalise)

    def get_by_contrato(
        self,
        contrato_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[LogsAnalise], int]:
        """
        Get logs by contract ID.

        Args:
            contrato_id: Contract ID
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (logs list, total count)
        """
        query = self.db.query(LogsAnalise).filter(
            LogsAnalise.contrato_id == contrato_id
        ).order_by(desc(LogsAnalise.criado_em))
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        return logs, total

    def get_by_usuario(
        self,
        usuario_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[LogsAnalise], int]:
        """
        Get logs by user ID.

        Args:
            usuario_id: User ID
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (logs list, total count)
        """
        query = self.db.query(LogsAnalise).filter(
            LogsAnalise.usuario_id == usuario_id
        ).order_by(desc(LogsAnalise.criado_em))
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        return logs, total

    def get_by_tipo_evento(
        self,
        tipo_evento: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[LogsAnalise], int]:
        """
        Get logs by event type.

        Args:
            tipo_evento: Event type (UPLOAD, PROCESSANDO, SUCESSO, ERRO)
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (logs list, total count)
        """
        query = self.db.query(LogsAnalise).filter(
            LogsAnalise.tipo_evento == tipo_evento
        ).order_by(desc(LogsAnalise.criado_em))
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        return logs, total

    def get_errors(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[LogsAnalise], int]:
        """
        Get error logs only.

        Args:
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (logs list, total count)
        """
        return self.get_by_tipo_evento("ERRO", skip, limit)

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[LogsAnalise], int]:
        """
        Get logs within date range.

        Args:
            start_date: Start date
            end_date: End date
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (logs list, total count)
        """
        query = self.db.query(LogsAnalise).filter(
            and_(
                LogsAnalise.criado_em >= start_date,
                LogsAnalise.criado_em <= end_date
            )
        ).order_by(desc(LogsAnalise.criado_em))
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        return logs, total

    def get_contrato_timeline(
        self,
        contrato_id: int
    ) -> List[LogsAnalise]:
        """
        Get complete timeline of a contract (all logs in order).

        Args:
            contrato_id: Contract ID

        Returns:
            List of logs in chronological order
        """
        return self.db.query(LogsAnalise).filter(
            LogsAnalise.contrato_id == contrato_id
        ).order_by(LogsAnalise.criado_em).all()

    def get_recent_errors(
        self,
        days: int = 7,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[LogsAnalise], int]:
        """
        Get recent error logs.

        Args:
            days: Number of days back
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (logs list, total count)
        """
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(LogsAnalise).filter(
            and_(
                LogsAnalise.tipo_evento == "ERRO",
                LogsAnalise.criado_em >= start_date
            )
        ).order_by(desc(LogsAnalise.criado_em))
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        return logs, total

    def search_by_mensagem(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[LogsAnalise], int]:
        """
        Search logs by message content.

        Args:
            search_term: Search string
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (logs list, total count)
        """
        query = self.db.query(LogsAnalise).filter(
            LogsAnalise.mensagem.ilike(f"%{search_term}%")
        ).order_by(desc(LogsAnalise.criado_em))
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        return logs, total

    def get_statistics(self) -> dict:
        """
        Get statistics about logs.

        Returns:
            Dictionary with statistics
        """
        from sqlalchemy import func
        
        total = self.count()
        
        type_counts = self.db.query(
            LogsAnalise.tipo_evento,
            func.count(LogsAnalise.id)
        ).group_by(LogsAnalise.tipo_evento).all()
        
        error_count = self.db.query(LogsAnalise).filter(
            LogsAnalise.tipo_evento == "ERRO"
        ).count()
        
        return {
            "total": total,
            "by_tipo": {tipo: count for tipo, count in type_counts},
            "erro_count": error_count,
        }

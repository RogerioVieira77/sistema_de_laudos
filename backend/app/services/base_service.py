"""
Base Service - Common service functionality
"""

from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class BaseService:
    """Base service class with common functionality"""

    def __init__(self, db: Session):
        """
        Initialize service with database session.

        Args:
            db: SQLAlchemy session
        """
        self.db = db

    def log_info(self, message: str):
        """Log info message"""
        logger.info(message)

    def log_error(self, message: str, exc: Exception = None):
        """Log error message"""
        if exc:
            logger.error(f"{message}: {str(exc)}")
        else:
            logger.error(message)

    def log_warning(self, message: str):
        """Log warning message"""
        logger.warning(message)

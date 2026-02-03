"""
Base Repository Pattern - Data Access Layer
"""

from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy import desc
from abc import ABC, abstractmethod

# Generic type for model
T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Base repository with common CRUD operations.
    All repositories should inherit from this class.
    """

    def __init__(self, db: Session, model: Type[T]):
        """
        Initialize repository with database session and model.

        Args:
            db: SQLAlchemy session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model

    def create(self, obj_in: dict) -> T:
        """
        Create a new object in the database.

        Args:
            obj_in: Dictionary with object data

        Returns:
            Created object
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: int) -> Optional[T]:
        """
        Get object by primary key.

        Args:
            id: Primary key value

        Returns:
            Object or None if not found
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[T], int]:
        """
        Get all objects with pagination.

        Args:
            skip: Number of objects to skip
            limit: Maximum number of objects to return

        Returns:
            Tuple of (objects list, total count)
        """
        query = self.db.query(self.model)
        total = query.count()
        objects = query.offset(skip).limit(limit).all()
        return objects, total

    def update(self, id: int, obj_in: dict) -> Optional[T]:
        """
        Update an object in the database.

        Args:
            id: Primary key value
            obj_in: Dictionary with updated data

        Returns:
            Updated object or None if not found
        """
        db_obj = self.get_by_id(id)
        if db_obj:
            for key, value in obj_in.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        """
        Delete an object from the database.

        Args:
            id: Primary key value

        Returns:
            True if deleted, False if not found
        """
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        """
        Count total objects in the table.

        Returns:
            Total count
        """
        return self.db.query(self.model).count()

    def exists(self, **kwargs) -> bool:
        """
        Check if an object exists based on filters.

        Args:
            **kwargs: Filter conditions

        Returns:
            True if exists, False otherwise
        """
        query = self.db.query(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first() is not None

"""
Usuario Repository - Data Access Layer for Usuario model
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.usuario import Usuario
from .base_repository import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    """Repository for Usuario model"""

    def __init__(self, db: Session):
        super().__init__(db, Usuario)

    def get_by_email(self, email: str) -> Optional[Usuario]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            Usuario object or None
        """
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def get_by_keycloak_id(self, keycloak_id: str) -> Optional[Usuario]:
        """
        Get user by Keycloak ID.

        Args:
            keycloak_id: Keycloak user ID

        Returns:
            Usuario object or None
        """
        return self.db.query(Usuario).filter(Usuario.keycloak_id == keycloak_id).first()

    def get_active_users(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Usuario], int]:
        """
        Get all active users.

        Args:
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (users list, total count)
        """
        query = self.db.query(Usuario).filter(Usuario.ativo == True)
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        return users, total

    def search_by_name_or_email(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Usuario], int]:
        """
        Search users by name or email.

        Args:
            search_term: Search string
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (users list, total count)
        """
        query = self.db.query(Usuario).filter(
            or_(
                Usuario.nome.ilike(f"%{search_term}%"),
                Usuario.email.ilike(f"%{search_term}%")
            )
        )
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        return users, total

    def get_by_cargo(
        self,
        cargo: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Usuario], int]:
        """
        Get users by cargo/role.

        Args:
            cargo: Cargo/role name
            skip: Number to skip
            limit: Limit results

        Returns:
            Tuple of (users list, total count)
        """
        query = self.db.query(Usuario).filter(Usuario.cargo == cargo)
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        return users, total

    def deactivate(self, usuario_id: int) -> Optional[Usuario]:
        """
        Deactivate a user.

        Args:
            usuario_id: User ID

        Returns:
            Updated user or None
        """
        return self.update(usuario_id, {"ativo": False})

    def activate(self, usuario_id: int) -> Optional[Usuario]:
        """
        Activate a user.

        Args:
            usuario_id: User ID

        Returns:
            Updated user or None
        """
        return self.update(usuario_id, {"ativo": True})

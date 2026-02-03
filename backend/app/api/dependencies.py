"""
Dependency Injection for API Endpoints
Provides: Database sessions, authentication, authorization
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Generator
import os
from dotenv import load_dotenv

from app.models.database import SessionLocal

load_dotenv()


def get_db() -> Generator:
    """
    Dependency for database session injection.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


async def get_current_user(
    authorization: str = None,
) -> int:
    """
    Validates JWT token and returns user_id.
    
    For MVP: Using a simple header validation.
    In production: Use python-jose with proper JWT validation.
    
    Args:
        authorization: Bearer token from Authorization header
        
    Returns:
        user_id (int): ID do usuário autenticado
        
    Raises:
        HTTPException: 401 se token inválido ou ausente
        
    Usage:
        @app.get("/items")
        async def get_items(user_id: int = Depends(get_current_user)):
            return {"user_id": user_id}
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Simple validation: Accept any token with format "Bearer <user_id>"
        # In production, implement proper JWT validation here
        scheme, credentials = authorization.split()
        
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
        
        # For MVP, extract user_id from token
        # Expected format: "Bearer <user_id>" or "Bearer jwt_token"
        # TODO: Replace with proper JWT validation using python-jose
        try:
            user_id = int(credentials)
        except ValueError:
            # If not a simple int, treat as JWT token
            # For now, extract from token claims (when JWT validation is added)
            user_id = 1  # Default user for MVP
        
        return user_id
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    authorization: str = None,
) -> int | None:
    """
    Optional authentication - returns user_id if token is valid, None otherwise.
    
    Usage:
        @app.get("/public-items")
        async def get_public_items(user_id: int | None = Depends(get_current_user_optional)):
            # Can be accessed with or without authentication
            return {"items": [...], "user_id": user_id}
    """
    if not authorization:
        return None
    
    try:
        scheme, credentials = authorization.split()
        
        if scheme.lower() != "bearer":
            return None
        
        try:
            user_id = int(credentials)
        except ValueError:
            user_id = 1  # Default for MVP
        
        return user_id
        
    except Exception:
        return None

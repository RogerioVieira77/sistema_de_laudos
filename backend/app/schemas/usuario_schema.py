"""
Usuario Schemas (DTOs)
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UsuarioBase(BaseModel):
    """Base schema for Usuario"""
    email: EmailStr
    nome: str = Field(..., min_length=1, max_length=255)
    cargo: Optional[str] = Field(None, max_length=100)
    ativo: bool = True


class UsuarioCreate(UsuarioBase):
    """Schema for creating a new Usuario"""
    keycloak_id: str = Field(..., min_length=1, max_length=255)


class UsuarioUpdate(BaseModel):
    """Schema for updating a Usuario"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    cargo: Optional[str] = Field(None, max_length=100)
    ativo: Optional[bool] = None


class UsuarioResponse(UsuarioBase):
    """Schema for Usuario response"""
    id: int
    keycloak_id: str
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class UsuarioListResponse(BaseModel):
    """Schema for Usuario list response"""
    total: int
    usuarios: list[UsuarioResponse]

    class Config:
        from_attributes = True

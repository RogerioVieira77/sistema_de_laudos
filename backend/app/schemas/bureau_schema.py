"""
DadosBureau Schemas (DTOs)
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class DadosBureauBase(BaseModel):
    """Base schema for DadosBureau"""
    cpf_cliente: str = Field(..., pattern=r'^\d{11}$', description="CPF com 11 dígitos")
    nome_cliente: str = Field(..., min_length=1, max_length=255)
    logradouro: str = Field(..., min_length=1)
    telefone: Optional[str] = Field(None, max_length=20)
    cep: Optional[str] = Field(None, pattern=r'^\d{8}$', description="CEP com 8 dígitos")


class DadosBureauCreate(DadosBureauBase):
    """Schema for creating bureau data"""
    contrato_id: int
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    data_consulta: Optional[datetime] = None


class DadosBureauUpdate(BaseModel):
    """Schema for updating bureau data"""
    nome_cliente: Optional[str] = Field(None, min_length=1, max_length=255)
    logradouro: Optional[str] = Field(None, min_length=1)
    telefone: Optional[str] = Field(None, max_length=20)
    cep: Optional[str] = Field(None, pattern=r'^\d{8}$')
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    data_consulta: Optional[datetime] = None


class DadosBureauResponse(DadosBureauBase):
    """Schema for DadosBureau response"""
    id: int
    contrato_id: int
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    data_consulta: Optional[datetime] = None
    criado_em: datetime

    class Config:
        from_attributes = True


class DadosBureauListResponse(BaseModel):
    """Schema for bureau data list response"""
    total: int
    dados: list[DadosBureauResponse]

    class Config:
        from_attributes = True

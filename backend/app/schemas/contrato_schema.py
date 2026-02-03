"""
DadosContrato Schemas (DTOs)
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class DadosContratoBase(BaseModel):
    """Base schema for DadosContrato"""
    cpf_cliente: str = Field(..., pattern=r'^\d{11}$', description="CPF com 11 dígitos")
    numero_contrato: str = Field(..., min_length=1, max_length=50)
    endereco_assinatura: Optional[str] = Field(None, max_length=500)
    status: str = Field(default="RECEBIDO", max_length=20)


class DadosContratoCreate(BaseModel):
    """Schema for uploading a contract"""
    usuario_id: int
    cpf_cliente: str = Field(..., pattern=r'^\d{11}$', description="CPF com 11 dígitos")
    numero_contrato: str = Field(..., min_length=1, max_length=50)
    endereco_assinatura: Optional[str] = Field(None, max_length=500)
    arquivo_pdf_path: str = Field(..., min_length=1, max_length=500)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class DadosContratoUpdate(BaseModel):
    """Schema for updating a contract"""
    endereco_assinatura: Optional[str] = Field(None, max_length=500)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    status: Optional[str] = Field(None, max_length=20)


class DadosContratoResponse(DadosContratoBase):
    """Schema for DadosContrato response"""
    id: int
    usuario_id: int
    arquivo_pdf_path: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class DadosContratoListResponse(BaseModel):
    """Schema for contract list response"""
    total: int
    page: int
    limit: int
    contratos: list[DadosContratoResponse]

    class Config:
        from_attributes = True

"""
Parecer Schemas (DTOs)
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
from decimal import Decimal


class PareceBase(BaseModel):
    """Base schema for Parecer"""
    contrato_id: int
    distancia_km: Decimal = Field(..., gt=0)
    tipo_parecer: Literal["PROXIMAL", "MODERADO", "DISTANTE", "MUITO_DISTANTE"]
    texto_parecer: str = Field(..., min_length=1)
    latitude_inicio: Decimal
    longitude_inicio: Decimal
    latitude_fim: Decimal
    longitude_fim: Decimal


class PareceCreate(PareceBase):
    """Schema for creating a parecer"""
    pass


class PareceUpdate(BaseModel):
    """Schema for updating a parecer"""
    texto_parecer: Optional[str] = Field(None, min_length=1)


class PareceResponse(PareceBase):
    """Schema for Parecer response"""
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True


class PareceListResponse(BaseModel):
    """Schema for parecer list response with pagination"""
    total: int
    page: int
    limit: int
    pareceres: list[PareceResponse]

    class Config:
        from_attributes = True


class PareceFilterRequest(BaseModel):
    """Schema for filtering pareceres"""
    tipo_parecer: Optional[Literal["PROXIMAL", "MODERADO", "DISTANTE", "MUITO_DISTANTE"]] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    distancia_minima: Optional[Decimal] = Field(None, gt=0)
    distancia_maxima: Optional[Decimal] = Field(None, gt=0)
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)

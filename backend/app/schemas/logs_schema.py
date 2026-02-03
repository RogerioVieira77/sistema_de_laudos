"""
LogsAnalise Schemas (DTOs)
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class LogsAnaliseBase(BaseModel):
    """Base schema for LogsAnalise"""
    contrato_id: int
    usuario_id: Optional[int] = None
    tipo_evento: Literal["UPLOAD", "PROCESSANDO", "SUCESSO", "ERRO"]
    mensagem: str = Field(..., min_length=1, max_length=500)
    detalhes: Optional[str] = None


class LogsAnaliseCreate(LogsAnaliseBase):
    """Schema for creating a log"""
    pass


class LogsAnaliseResponse(LogsAnaliseBase):
    """Schema for LogsAnalise response"""
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True


class LogsAnaliseListResponse(BaseModel):
    """Schema for logs list response"""
    total: int
    page: int
    limit: int
    logs: list[LogsAnaliseResponse]

    class Config:
        from_attributes = True


class LogsAnaliseFilterRequest(BaseModel):
    """Schema for filtering logs"""
    contrato_id: Optional[int] = None
    usuario_id: Optional[int] = None
    tipo_evento: Optional[Literal["UPLOAD", "PROCESSANDO", "SUCESSO", "ERRO"]] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

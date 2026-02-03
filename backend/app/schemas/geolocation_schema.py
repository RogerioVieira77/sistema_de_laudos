"""
Geolocalização Schemas (DTOs)
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class GeolocationRequest(BaseModel):
    """Schema for geolocation analysis request"""
    contrato_id: int


class GeolocationAnalysisResponse(BaseModel):
    """Schema for geolocation analysis response"""
    contrato_id: int
    endereco_origem: str
    endereco_destino: str
    latitude_origem: Decimal
    longitude_origem: Decimal
    latitude_destino: Decimal
    longitude_destino: Decimal
    distancia_km: Decimal
    tipo_parecer: str
    texto_parecer: str
    rota: Optional[list[list[Decimal]]] = Field(None, description="Array de coordenadas [lat, lng]")
    timestamp: datetime

    class Config:
        from_attributes = True


class CoordenadasRequest(BaseModel):
    """Schema for coordinates request"""
    latitude: Decimal
    longitude: Decimal


class DistanceCalculationRequest(BaseModel):
    """Schema for distance calculation"""
    latitude_origem: Decimal
    longitude_origem: Decimal
    latitude_destino: Decimal
    longitude_destino: Decimal


class DistanceCalculationResponse(BaseModel):
    """Schema for distance calculation response"""
    distancia_km: Decimal
    distancia_metros: Decimal
    tempo_estimado_horas: Optional[Decimal] = None

    class Config:
        from_attributes = True

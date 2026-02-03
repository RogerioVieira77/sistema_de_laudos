"""
Parecer Model
"""

from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Index, Text
from datetime import datetime
from .database import Base


class Parecer(Base):
    """
    Análises e pareceres gerados baseados em geolocalização
    
    Attributes:
        id: Identificador único
        contrato_id: FK para DadosContrato
        distancia_km: Distância calculada entre pontos (Haversine)
        tipo_parecer: Classificação (PROXIMAL, MODERADO, DISTANTE, MUITO_DISTANTE)
        texto_parecer: Texto automático do parecer
        latitude_inicio: Latitude do ponto de origem (contrato)
        longitude_inicio: Longitude do ponto de origem (contrato)
        latitude_fim: Latitude do ponto de destino (bureau)
        longitude_fim: Longitude do ponto de destino (bureau)
        criado_em: Timestamp de criação
    """
    
    __tablename__ = "pareceres"
    
    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey("dados_contrato.id", ondelete="CASCADE"), nullable=False, unique=True)
    distancia_km = Column(Numeric(precision=10, scale=2), nullable=False)
    tipo_parecer = Column(String(20), nullable=False, index=True)  # PROXIMAL, MODERADO, DISTANTE, MUITO_DISTANTE
    texto_parecer = Column(Text, nullable=False)
    latitude_inicio = Column(Numeric(precision=10, scale=8), nullable=False)
    longitude_inicio = Column(Numeric(precision=11, scale=8), nullable=False)
    latitude_fim = Column(Numeric(precision=10, scale=8), nullable=False)
    longitude_fim = Column(Numeric(precision=11, scale=8), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Índices
    __table_args__ = (
        Index("idx_parecer_contrato_id", "contrato_id"),
        Index("idx_parecer_tipo", "tipo_parecer"),
        Index("idx_parecer_criado_em", "criado_em"),
    )
    
    def __repr__(self):
        return f"<Parecer(id={self.id}, contrato_id={self.contrato_id}, tipo={self.tipo_parecer}, dist={self.distancia_km}km)>"

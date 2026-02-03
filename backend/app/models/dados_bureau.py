"""
DadosBureau Model
"""

from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Index, Text
from datetime import datetime
from .database import Base


class DadosBureau(Base):
    """
    Informações do cliente de bureau externo
    
    Attributes:
        id: Identificador único
        contrato_id: FK para DadosContrato
        cpf_cliente: CPF do cliente (chave de busca)
        nome_cliente: Nome do cliente conforme bureau
        logradouro: Rua/avenida
        telefone: Telefone do cliente
        cep: CEP do endereço
        latitude: Latitude obtida via Nominatim (coordenada de destino)
        longitude: Longitude obtida via Nominatim (coordenada de destino)
        data_consulta: Data da consulta ao bureau
        criado_em: Timestamp de criação
    """
    
    __tablename__ = "dados_bureau"
    
    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey("dados_contrato.id", ondelete="CASCADE"), nullable=False)
    cpf_cliente = Column(String(11), nullable=False, index=True)
    nome_cliente = Column(String(255), nullable=False)
    logradouro = Column(Text, nullable=False)
    telefone = Column(String(20), nullable=True)
    cep = Column(String(8), nullable=True)
    latitude = Column(Numeric(precision=10, scale=8), nullable=True)
    longitude = Column(Numeric(precision=11, scale=8), nullable=True)
    data_consulta = Column(DateTime, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Índices
    __table_args__ = (
        Index("idx_dados_bureau_contrato_id", "contrato_id"),
        Index("idx_dados_bureau_cpf", "cpf_cliente"),
        Index("idx_dados_bureau_criado_em", "criado_em"),
    )
    
    def __repr__(self):
        return f"<DadosBureau(id={self.id}, cpf={self.cpf_cliente}, nome={self.nome_cliente})>"

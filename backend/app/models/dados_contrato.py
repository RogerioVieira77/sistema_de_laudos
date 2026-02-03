"""
DadosContrato Model
"""

from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Index, Text
from datetime import datetime
from .database import Base


class DadosContrato(Base):
    """
    Informações extraídas do PDF do contrato
    
    Attributes:
        id: Identificador único
        usuario_id: FK para o usuário que fez upload
        cpf_cliente: CPF do cliente (extraído do PDF)
        numero_contrato: Número do contrato (extraído do PDF)
        latitude: Latitude do endereço de assinatura (coordenada de origem)
        longitude: Longitude do endereço de assinatura (coordenada de origem)
        endereco_assinatura: Endereço onde o contrato foi assinado
        arquivo_pdf_path: Caminho do arquivo PDF armazenado
        status: Status do processamento (RECEBIDO, PROCESSANDO, CONCLUIDO, ERRO)
        criado_em: Timestamp de criação
        atualizado_em: Timestamp da última atualização
    """
    
    __tablename__ = "dados_contrato"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    cpf_cliente = Column(String(11), nullable=False, index=True)
    numero_contrato = Column(String(50), nullable=False, index=True)
    latitude = Column(Numeric(precision=10, scale=8), nullable=True)
    longitude = Column(Numeric(precision=11, scale=8), nullable=True)
    endereco_assinatura = Column(Text, nullable=True)
    arquivo_pdf_path = Column(String(500), nullable=False)
    status = Column(String(20), default="RECEBIDO", nullable=False, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Índices
    __table_args__ = (
        Index("idx_dados_contrato_usuario_id", "usuario_id"),
        Index("idx_dados_contrato_cpf", "cpf_cliente"),
        Index("idx_dados_contrato_numero", "numero_contrato"),
        Index("idx_dados_contrato_status", "status"),
        Index("idx_dados_contrato_criado_em", "criado_em"),
    )
    
    def __repr__(self):
        return f"<DadosContrato(id={self.id}, cpf={self.cpf_cliente}, contrato={self.numero_contrato})>"

"""
LogsAnalise Model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Text
from datetime import datetime
from .database import Base


class LogsAnalise(Base):
    """
    Rastreamento e logs de análises realizadas
    
    Attributes:
        id: Identificador único
        contrato_id: FK para DadosContrato
        usuario_id: FK para Usuario
        tipo_evento: Tipo de evento (UPLOAD, PROCESSANDO, SUCESSO, ERRO)
        mensagem: Mensagem descritiva do evento
        detalhes: Detalhes adicionais em JSON ou texto
        criado_em: Timestamp do evento
    """
    
    __tablename__ = "logs_analise"
    
    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey("dados_contrato.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    tipo_evento = Column(String(20), nullable=False, index=True)  # UPLOAD, PROCESSANDO, SUCESSO, ERRO
    mensagem = Column(String(500), nullable=False)
    detalhes = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Índices
    __table_args__ = (
        Index("idx_logs_analise_contrato_id", "contrato_id"),
        Index("idx_logs_analise_usuario_id", "usuario_id"),
        Index("idx_logs_analise_tipo_evento", "tipo_evento"),
        Index("idx_logs_analise_criado_em", "criado_em"),
    )
    
    def __repr__(self):
        return f"<LogsAnalise(id={self.id}, contrato_id={self.contrato_id}, tipo={self.tipo_evento})>"

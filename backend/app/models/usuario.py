"""
Usuario Model
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from datetime import datetime
from .database import Base


class Usuario(Base):
    """
    Usuários do Sistema de Laudos
    
    Attributes:
        id: Identificador único do usuário
        keycloak_id: ID do usuário no Keycloak
        email: Email do usuário (único)
        nome: Nome completo
        cargo: Cargo/função do usuário
        ativo: Flag indicando se o usuário está ativo
        criado_em: Timestamp de criação
        atualizado_em: Timestamp da última atualização
    """
    
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    keycloak_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    cargo = Column(String(100), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Índices
    __table_args__ = (
        Index("idx_usuario_keycloak_id", "keycloak_id"),
        Index("idx_usuario_email", "email"),
        Index("idx_usuario_ativo", "ativo"),
    )
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, nome={self.nome})>"

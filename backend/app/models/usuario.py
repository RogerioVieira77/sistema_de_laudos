"""
Usuario Model
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index, ForeignKey
from datetime import datetime
from .database import Base


class Usuario(Base):
    """
    Usuários do Sistema de Laudos
    
    Attributes:
        id: Identificador único do usuário
        keycloak_id: ID do usuário no Keycloak (sub claim do JWT)
        email: Email do usuário (único)
        nome: Nome completo
        cargo: Cargo/função do usuário
        tenant_id: ID do tenant para multi-tenancy (isolação de dados)
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
    tenant_id = Column(
        String(36),
        nullable=False,
        default="default",
        index=True,
        doc="ID do tenant para multi-tenancy (isolação de dados)"
    )
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Índices
    __table_args__ = (
        Index("idx_usuario_keycloak_id", "keycloak_id"),
        Index("idx_usuario_email", "email"),
        Index("idx_usuario_ativo", "ativo"),
        Index("idx_usuario_tenant_id", "tenant_id"),
        Index("idx_usuario_tenant_email", "tenant_id", "email"),
    )
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, nome={self.nome}, tenant={self.tenant_id})>"
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            "id": self.id,
            "keycloak_id": self.keycloak_id,
            "email": self.email,
            "nome": self.nome,
            "cargo": self.cargo,
            "tenant_id": self.tenant_id,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }

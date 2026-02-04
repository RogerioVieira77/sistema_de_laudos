"""
Tenant Model - Modelo para multi-tenancy
Representa uma organização/cliente no sistema
Autor: Sistema de Laudos
Data: 2024-02-03
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class Tenant(Base):
    """
    Modelo de Tenant para suportar multi-tenancy
    
    Cada tenant representa uma organização/cliente separado
    com dados isolados automaticamente
    
    Attributes:
        id: UUID único do tenant
        name: Nome da organização/cliente
        description: Descrição do tenant
        active: Se o tenant está ativo ou não
        created_at: Data de criação
        updated_at: Data da última atualização
    """
    
    __tablename__ = "tenants"
    
    # Identificação
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="UUID único do tenant"
    )
    
    # Informações do tenant
    name = Column(
        String(255),
        nullable=False,
        index=True,
        doc="Nome da organização/cliente"
    )
    
    description = Column(
        String(500),
        nullable=True,
        doc="Descrição do tenant (opcional)"
    )
    
    # Status
    active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        doc="Se o tenant está ativo (soft delete via flag)"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="Data de criação do tenant"
    )
    
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="Data da última atualização"
    )
    
    # Índices compostos para performance
    __table_args__ = (
        Index('ix_tenants_active', 'active'),
        Index('ix_tenants_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, name={self.name}, active={self.active})>"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.id})"
    
    def to_dict(self) -> dict:
        """Converter para dicionário"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def create_default(cls) -> "Tenant":
        """Criar tenant padrão para compatibilidade com versões antigas"""
        return cls(
            id="default",
            name="Default Tenant",
            description="Tenant padrão para usuários sem tenant específico",
            active=True,
        )

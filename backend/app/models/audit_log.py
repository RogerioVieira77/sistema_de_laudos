"""
AuditLog Model - Registro de auditoria para compliance e segurança
Rastreia todas as ações dos usuários no sistema
Autor: Sistema de Laudos
Data: 2024-02-03
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSON
import uuid
import enum
import json

from .database import Base


class AuditAction(str, enum.Enum):
    """Tipos de ações auditadas"""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    EXPORT = "EXPORT"
    DOWNLOAD = "DOWNLOAD"
    UPLOAD = "UPLOAD"
    EXECUTE = "EXECUTE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"


class AuditStatus(str, enum.Enum):
    """Status da ação auditada"""
    SUCCESS = "success"
    ERROR = "error"
    BLOCKED = "blocked"  # Bloqueado por segurança/permissões


class AuditLog(Base):
    """
    Modelo de registro de auditoria
    
    Rastreia todas as ações importantes do sistema para:
    - Compliance (LGPD, etc)
    - Segurança (detectar anomalias)
    - Debugging (reproduzir problemas)
    - Analytics (entender uso do sistema)
    
    Attributes:
        id: UUID único do log
        user_id: ID do usuário que executou a ação
        user_email: Email do usuário (desnormalizado para auditar deletados)
        tenant_id: ID do tenant (para isolação multi-tenant)
        action: Tipo de ação (CREATE, READ, UPDATE, DELETE, EXPORT, etc)
        resource_type: Tipo de recurso afetado (contrato, parecer, bureau, etc)
        resource_id: ID do recurso específico afetado
        status: Status da ação (success, error, blocked)
        error_message: Mensagem de erro se falhou
        ip_address: IP do cliente que fez a ação
        user_agent: User-Agent do navegador/cliente
        details: Dados adicionais em JSON (filtros, parametros, etc)
        timestamp: Data/hora da ação (para auditoria)
        created_at: Data de criação do log
    """
    
    __tablename__ = "audit_logs"
    
    # Identificação
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="UUID único do log de auditoria"
    )
    
    # Usuário e contexto
    user_id = Column(
        String(36),
        nullable=False,
        index=True,
        doc="ID do usuário que executou a ação (sub do JWT)"
    )
    
    user_email = Column(
        String(255),
        nullable=True,
        index=True,
        doc="Email do usuário (desnormalizado para rastrear usuários deletados)"
    )
    
    # Multi-tenancy
    tenant_id = Column(
        String(36),
        nullable=False,
        index=True,
        default="default",
        doc="ID do tenant (para isolação de dados)"
    )
    
    # Ação auditada
    action = Column(
        SQLEnum(AuditAction),
        nullable=False,
        index=True,
        doc="Tipo de ação: CREATE, READ, UPDATE, DELETE, EXPORT, DOWNLOAD, UPLOAD"
    )
    
    resource_type = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Tipo de recurso afetado: contrato, parecer, bureau, usuario, etc"
    )
    
    resource_id = Column(
        String(36),
        nullable=True,
        index=True,
        doc="ID do recurso específico afetado (se aplicável)"
    )
    
    # Resultado da ação
    status = Column(
        SQLEnum(AuditStatus),
        nullable=False,
        default=AuditStatus.SUCCESS,
        index=True,
        doc="Status: success, error, blocked"
    )
    
    error_message = Column(
        String(500),
        nullable=True,
        doc="Mensagem de erro se a ação falhou ou foi bloqueada"
    )
    
    # Contexto HTTP
    ip_address = Column(
        String(45),  # IPv6 pode ter até 45 caracteres
        nullable=True,
        index=True,
        doc="IP do cliente (para detecção de anomalias)"
    )
    
    user_agent = Column(
        String(500),
        nullable=True,
        doc="User-Agent do navegador/cliente"
    )
    
    # Dados adicionais
    details = Column(
        JSON,
        nullable=True,
        doc="Dados adicionais em JSON (filtros usados, parâmetros, etc)"
    )
    
    # Timestamps
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        doc="Data/hora exata da ação (para auditoria)"
    )
    
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="Data de criação do registro"
    )
    
    # Índices compostos para queries comuns
    __table_args__ = (
        # Índice para queries por tenant + ação + timestamp
        Index(
            'ix_audit_logs_tenant_action_timestamp',
            'tenant_id', 'action', 'timestamp',
            unique=False
        ),
        # Índice para queries por usuário + timestamp
        Index(
            'ix_audit_logs_user_timestamp',
            'user_id', 'timestamp',
            unique=False
        ),
        # Índice para queries por resource_type + resource_id
        Index(
            'ix_audit_logs_resource',
            'resource_type', 'resource_id',
            unique=False
        ),
        # Índice para cleanup automático de logs antigos
        Index(
            'ix_audit_logs_timestamp_cleanup',
            'timestamp',
            unique=False
        ),
    )
    
    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, user={self.user_email}, "
            f"action={self.action}, resource={self.resource_type}, "
            f"status={self.status})>"
        )
    
    def __str__(self) -> str:
        return (
            f"{self.user_email} {self.action.value} {self.resource_type} "
            f"[{self.status.value}] @ {self.timestamp}"
        )
    
    def to_dict(self) -> dict:
        """Converter para dicionário"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "tenant_id": self.tenant_id,
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "status": self.status.value,
            "error_message": self.error_message,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def log_action(
        cls,
        user_id: str,
        user_email: str,
        action: AuditAction,
        resource_type: str,
        resource_id: str = None,
        tenant_id: str = "default",
        status: AuditStatus = AuditStatus.SUCCESS,
        error_message: str = None,
        ip_address: str = None,
        user_agent: str = None,
        details: dict = None,
    ) -> "AuditLog":
        """
        Factory method para criar e retornar um log de auditoria
        
        Args:
            user_id: ID do usuário
            user_email: Email do usuário
            action: Tipo de ação
            resource_type: Tipo de recurso
            resource_id: ID do recurso
            tenant_id: ID do tenant
            status: Status da ação
            error_message: Mensagem de erro se falhou
            ip_address: IP do cliente
            user_agent: User-Agent do cliente
            details: Dados adicionais
        
        Returns:
            Instância de AuditLog pronta para ser inserida no BD
        """
        return cls(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            tenant_id=tenant_id,
            status=status,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
        )

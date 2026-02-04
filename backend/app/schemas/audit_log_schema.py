"""
AuditLog Schemas
Schemas Pydantic para serialização de logs de auditoria
Autor: Sistema de Laudos
Data: 2024-02-03
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class AuditLogSchema(BaseModel):
    """Schema para um registro de auditoria individual"""
    
    id: str = Field(..., description="UUID único do log")
    user_id: str = Field(..., description="ID do usuário que executou a ação")
    user_email: str = Field(..., description="Email do usuário")
    tenant_id: str = Field(..., description="ID do tenant")
    
    action: str = Field(..., description="Tipo de ação: CREATE, READ, UPDATE, DELETE")
    resource_type: str = Field(..., description="Tipo de recurso: contrato, parecer, etc")
    resource_id: Optional[str] = Field(None, description="ID do recurso específico")
    
    status: str = Field(..., description="Status: success, error, blocked")
    error_message: Optional[str] = Field(None, description="Mensagem de erro se falhou")
    
    ip_address: Optional[str] = Field(None, description="IP do cliente")
    user_agent: Optional[str] = Field(None, description="User-Agent do navegador")
    
    details: Optional[dict] = Field(None, description="Dados adicionais em JSON")
    
    timestamp: datetime = Field(..., description="Data/hora da ação")
    created_at: datetime = Field(..., description="Data de criação do log")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user-uuid-1234",
                "user_email": "user@example.com",
                "tenant_id": "tenant-uuid-5678",
                "action": "CREATE",
                "resource_type": "contratos",
                "resource_id": "123",
                "status": "success",
                "error_message": None,
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "details": {
                    "method": "POST",
                    "path": "/api/v1/contratos",
                    "status_code": 201,
                    "duration_ms": 245.5,
                },
                "timestamp": "2024-02-03T10:30:00Z",
                "created_at": "2024-02-03T10:30:00Z",
            }
        }


class AuditLogListResponse(BaseModel):
    """Response para lista de logs"""
    
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros pulados")
    limit: int = Field(..., description="Limite de registros")
    items: List[AuditLogSchema] = Field(..., description="Lista de logs")


class AuditActivitySummary(BaseModel):
    """Resumo de atividades do tenant"""
    
    total_actions: int = Field(..., description="Total de ações")
    actions: dict = Field(..., description="Contagem por tipo de ação")
    statuses: dict = Field(..., description="Contagem por status")
    resources: dict = Field(..., description="Contagem por tipo de recurso")
    unique_users: int = Field(..., description="Número de usuários únicos")
    date_range: dict = Field(..., description="Período dos dados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_actions": 1523,
                "actions": {
                    "CREATE": 245,
                    "READ": 1000,
                    "UPDATE": 200,
                    "DELETE": 78,
                },
                "statuses": {
                    "success": 1500,
                    "error": 20,
                    "blocked": 3,
                },
                "resources": {
                    "contratos": 500,
                    "pareceres": 450,
                    "bureau": 350,
                    "usuarios": 223,
                },
                "unique_users": 45,
                "date_range": {
                    "from": "2024-01-04T10:30:00Z",
                    "to": "2024-02-03T10:30:00Z",
                },
            }
        }

"""
Audit Log API Endpoints
Rotas para acessar logs de auditoria (admin/compliance)
Autor: Sistema de Laudos
Data: 2024-02-03

Rate Limiting:
- GET /my-activity: 20 req/min (AUDIT)
- GET /tenant-activity: 5 req/min (ADMIN)
- GET /resource/{type}/{id}: 20 req/min (AUDIT)
- GET /failed-actions: 5 req/min (ADMIN)
- GET /activity-summary: 5 req/min (ADMIN)
- GET /suspicious-activity: 5 req/min (ADMIN)
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_audit_log_service
from app.api.decorators import require_roles, require_tenant
from app.api.rate_limiting import limiter, RateLimits
from app.core.oidc_models import Identity
from app.api.dependencies import get_identity
from app.schemas.audit_log_schema import (
    AuditLogSchema,
    AuditLogListResponse,
    AuditActivitySummary,
)
from app.services.audit_log_service import AuditLogService

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get(
    "/my-activity",
    response_model=AuditLogListResponse,
    summary="Obter meu histórico de atividades",
    description="Retorna um log de todas as ações que o usuário autenticado realizou",
    responses={
        200: {"description": "Histórico de atividades do usuário"},
        429: {"description": "Muitas requisições. Limite: 20 por minuto"},
    }
)
@require_tenant()
@limiter.limit(RateLimits.AUDIT)
async def get_my_activity(
    request: Request,  # Necessário para rate limiting
    identity: Identity = Depends(get_identity),
    service: AuditLogService = Depends(get_audit_log_service),
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    days_back: int = Query(90, ge=1, le=365, description="Dias para olhar para trás"),
):
    """
    Retorna o histórico de atividades do usuário autenticado.
    
    Requer autenticação (JWT Bearer token).
    
    Rate limit: 20 requisições por minuto
    
    ### Query Parameters:
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Máximo de registros a retornar (padrão: 100, máx: 1000)
    - **days_back**: Dias para olhar para trás (padrão: 90)
    
    ### Response:
    - Lista de logs de auditoria do usuário
    """
    logs = service.get_user_activity(
        user_id=identity.sub,
        limit=limit,
        skip=skip,
        days_back=days_back,
    )
    
    total = len(logs)  # Nota: idealmente isso seria uma count query
    
    return AuditLogListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[AuditLogSchema.from_attributes(log) for log in logs],
    )


@router.get(
    "/tenant-activity",
    response_model=AuditLogListResponse,
    summary="Obter atividades do tenant",
    description="Retorna logs de auditoria de todo o tenant (requer role admin)",
    responses={
        200: {"description": "Logs de atividades do tenant"},
        429: {"description": "Muitas requisições. Limite: 5 por minuto"},
    }
)
@require_tenant()
@require_roles("admin")
@limiter.limit(RateLimits.ADMIN)
async def get_tenant_activity(
    request: Request,  # Necessário para rate limiting
    identity: Identity = Depends(get_identity),
    service: AuditLogService = Depends(get_audit_log_service),
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    days_back: int = Query(30, ge=1, le=365, description="Dias para olhar para trás"),
    action: Optional[str] = Query(None, description="Filtrar por ação (CREATE, READ, UPDATE, DELETE)"),
    status: Optional[str] = Query(None, description="Filtrar por status (success, error, blocked)"),
):
    """
    Retorna logs de auditoria de todo o tenant.
    
    Requer autenticação (JWT Bearer token) + role 'admin'.
    
    Rate limit: 5 requisições por minuto
    
    ### Query Parameters:
    - **skip**: Número de registros a pular
    - **limit**: Máximo de registros (padrão: 100, máx: 1000)
    - **days_back**: Dias para olhar para trás (padrão: 30)
    - **action**: Filtrar por tipo de ação (opcional)
    - **status**: Filtrar por status (opcional)
    
    ### Response:
    - Lista de todos os logs do tenant
    """
    logs = service.get_tenant_activity(
        tenant_id=identity.tenant_id,
        limit=limit,
        skip=skip,
        days_back=days_back,
        action=action,
        status=status,
    )
    
    total = len(logs)  # Nota: idealmente isso seria uma count query
    
    return AuditLogListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[AuditLogSchema.from_attributes(log) for log in logs],
    )


@router.get(
    "/resource/{resource_type}/{resource_id}",
    response_model=AuditLogListResponse,
    summary="Obter histórico de um recurso",
    description="Retorna todos os logs relacionados a um recurso específico",
    responses={
        200: {"description": "Histórico do recurso"},
        429: {"description": "Muitas requisições. Limite: 20 por minuto"},
    }
)
@require_tenant()
@limiter.limit(RateLimits.AUDIT)
async def get_resource_history(
    request: Request,  # Necessário para rate limiting
    resource_type: str,
    resource_id: str,
    identity: Identity = Depends(get_identity),
    service: AuditLogService = Depends(get_audit_log_service),
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
):
    """
    Retorna o histórico de auditoria de um recurso específico.
    
    Útil para ver quem fez o quê em um contrato, parecer, etc.
    
    Requer autenticação (JWT Bearer token).
    
    Rate limit: 20 requisições por minuto
    
    ### Path Parameters:
    - **resource_type**: Tipo do recurso (contrato, parecer, bureau, etc)
    - **resource_id**: ID do recurso específico
    
    ### Query Parameters:
    - **skip**: Número de registros a pular
    - **limit**: Máximo de registros
    
    ### Response:
    - Histórico completo do recurso
    """
    logs = service.get_resource_history(
        resource_type=resource_type,
        resource_id=resource_id,
        limit=limit,
        skip=skip,
    )
    
    # Validar que logs pertencem ao tenant do usuário
    for log in logs:
        if log.tenant_id != identity.tenant_id:
            raise HTTPException(status_code=403, detail="Sem permissão")
    
    total = len(logs)
    
    return AuditLogListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[AuditLogSchema.from_attributes(log) for log in logs],
    )


@router.get(
    "/failed-actions",
    response_model=AuditLogListResponse,
    summary="Obter ações que falharam",
    description="Retorna ações com erro ou bloqueadas (para detectar tentativas de ataque)",
    responses={
        200: {"description": "Ações falhadas ou bloqueadas"},
        429: {"description": "Muitas requisições. Limite: 5 por minuto"},
    }
)
@require_tenant()
@require_roles("admin")
@limiter.limit(RateLimits.ADMIN)
async def get_failed_actions(
    request: Request,  # Necessário para rate limiting
    identity: Identity = Depends(get_identity),
    service: AuditLogService = Depends(get_audit_log_service),
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    days_back: int = Query(7, ge=1, le=30, description="Dias para olhar para trás"),
):
    """
    Retorna ações que falharam ou foram bloqueadas.
    
    Útil para detectar tentativas de acesso não autorizado ou anomalias de segurança.
    
    Requer autenticação + role 'admin'.
    
    Rate limit: 5 requisições por minuto
    
    ### Response:
    - Lista de ações falhadas/bloqueadas
    """
    logs = service.get_failed_actions(
        tenant_id=identity.tenant_id,
        limit=limit,
        skip=skip,
        days_back=days_back,
    )
    
    total = len(logs)
    
    return AuditLogListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[AuditLogSchema.from_attributes(log) for log in logs],
    )


@router.get(
    "/activity-summary",
    response_model=AuditActivitySummary,
    summary="Obter resumo de atividades",
    description="Retorna estatísticas de atividades do tenant",
    responses={
        200: {"description": "Resumo estatístico de atividades"},
        429: {"description": "Muitas requisições. Limite: 5 por minuto"},
    }
)
@require_tenant()
@require_roles("admin")
@limiter.limit(RateLimits.ADMIN)
async def get_activity_summary(
    request: Request,  # Necessário para rate limiting
    identity: Identity = Depends(get_identity),
    service: AuditLogService = Depends(get_audit_log_service),
    days_back: int = Query(30, ge=1, le=365, description="Dias para olhar para trás"),
):
    """
    Retorna um resumo estatístico das atividades do tenant.
    
    Inclui contagem por tipo de ação, status, recursos, usuários únicos, etc.
    
    Requer autenticação + role 'admin'.
    
    Rate limit: 5 requisições por minuto
    
    ### Response:
    - Resumo com estatísticas agregadas
    """
    return service.get_activity_summary(
        tenant_id=identity.tenant_id,
        days_back=days_back,
    )


@router.get(
    "/suspicious-activity",
    summary="Detectar atividade suspeita",
    description="Detecta IPs e usuários com muitas ações falhadas",
    responses={
        200: {"description": "Lista de atividades suspeitas"},
        429: {"description": "Muitas requisições. Limite: 5 por minuto"},
    }
)
@require_tenant()
@require_roles("admin")
@limiter.limit(RateLimits.ADMIN)
async def detect_suspicious_activity(
    request: Request,  # Necessário para rate limiting
    identity: Identity = Depends(get_identity),
    service: AuditLogService = Depends(get_audit_log_service),
    threshold: int = Query(10, ge=1, le=100, description="Limite de ações falhadas"),
):
    """
    Detecta atividade suspeita no tenant.
    
    Procura por IPs ou usuários com muitos erros/bloqueios nas últimas 24h.
    
    Requer autenticação + role 'admin'.
    
    Rate limit: 5 requisições por minuto
    
    ### Query Parameters:
    - **threshold**: Número de ações falhadas para considerar suspeito (padrão: 10)
    
    ### Response:
    - Lista de IPs/usuários suspeitos e contagem de ações falhadas
    """
    return service.detect_suspicious_activity(
        tenant_id=identity.tenant_id,
        threshold=threshold,
    )

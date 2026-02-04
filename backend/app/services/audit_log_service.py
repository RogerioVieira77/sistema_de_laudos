"""
AuditLog Service
Lógica de negócio para logs de auditoria
Autor: Sistema de Laudos
Data: 2024-02-03
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import AuditLog, AuditAction, AuditStatus
from app.repositories.audit_log_repository import AuditLogRepository
from app.core.exceptions import APIException


class AuditLogService:
    """Service para operações de auditoria"""
    
    def __init__(self, db: Session):
        self.repository = AuditLogRepository(db)
        self.db = db
    
    def log_action(
        self,
        user_id: str,
        user_email: str,
        action: AuditAction,
        resource_type: str,
        tenant_id: str = "default",
        resource_id: Optional[str] = None,
        status: AuditStatus = AuditStatus.SUCCESS,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> AuditLog:
        """
        Registrar uma ação na auditoria
        Chamado normalmente pelo middleware
        """
        return self.repository.create(
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
            details=details,
        )
    
    def get_user_activity(
        self,
        user_id: str,
        limit: int = 100,
        skip: int = 0,
        days_back: int = 90,
    ) -> List[AuditLog]:
        """
        Obter histórico de atividades de um usuário
        """
        return self.repository.get_by_user(
            user_id=user_id,
            limit=limit,
            skip=skip,
            days_back=days_back,
        )
    
    def get_tenant_activity(
        self,
        tenant_id: str,
        limit: int = 100,
        skip: int = 0,
        days_back: int = 90,
        action: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[AuditLog]:
        """
        Obter histórico de atividades de um tenant (admin/compliance)
        """
        # Converter strings para enums
        action_enum = None
        if action:
            try:
                action_enum = AuditAction(action.upper())
            except ValueError:
                raise APIException(
                    status_code=400,
                    detail=f"Ação inválida: {action}",
                )
        
        status_enum = None
        if status:
            try:
                status_enum = AuditStatus(status.lower())
            except ValueError:
                raise APIException(
                    status_code=400,
                    detail=f"Status inválido: {status}",
                )
        
        return self.repository.get_by_tenant(
            tenant_id=tenant_id,
            limit=limit,
            skip=skip,
            days_back=days_back,
            action=action_enum,
            status=status_enum,
        )
    
    def get_resource_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 100,
        skip: int = 0,
    ) -> List[AuditLog]:
        """
        Obter histórico de um recurso específico
        Exemplo: ver todas as ações feitas em um contrato
        """
        return self.repository.get_by_resource(
            resource_type=resource_type,
            resource_id=resource_id,
            limit=limit,
            skip=skip,
        )
    
    def get_failed_actions(
        self,
        tenant_id: str,
        limit: int = 100,
        skip: int = 0,
        days_back: int = 30,
    ) -> List[AuditLog]:
        """
        Obter ações que falharam (detectar tentativas de ataque)
        """
        return self.repository.get_failed_actions(
            tenant_id=tenant_id,
            limit=limit,
            skip=skip,
            days_back=days_back,
        )
    
    def get_ip_activity(
        self,
        tenant_id: str,
        ip_address: str,
        limit: int = 100,
        skip: int = 0,
        days_back: int = 7,
    ) -> List[AuditLog]:
        """
        Obter atividades de um IP específico
        """
        return self.repository.get_by_ip_address(
            ip_address=ip_address,
            limit=limit,
            skip=skip,
            days_back=days_back,
        )
    
    def get_activity_summary(
        self,
        tenant_id: str,
        days_back: int = 30,
    ) -> dict:
        """
        Obter resumo de atividades do tenant
        """
        return self.repository.get_activity_summary(
            tenant_id=tenant_id,
            days_back=days_back,
        )
    
    def cleanup_old_logs(self, days_retention: int = 365) -> int:
        """
        Limpar logs antigos (para compliance de retenção de dados)
        """
        return self.repository.cleanup_old_logs(days_retention=days_retention)
    
    def detect_suspicious_activity(
        self,
        tenant_id: str,
        threshold: int = 10,
    ) -> List[dict]:
        """
        Detectar atividade suspeita (muitos erros/bloqueios)
        Retorna lista de IPs e usuários suspeitos
        """
        # Buscar ações falhadas nas últimas 24 horas
        failed_logs = self.repository.get_failed_actions(
            tenant_id=tenant_id,
            days_back=1,
            limit=10000,
        )
        
        # Agrupar por IP
        ip_counts = {}
        for log in failed_logs:
            if log.ip_address:
                ip_counts[log.ip_address] = ip_counts.get(log.ip_address, 0) + 1
        
        # Agrupar por usuário
        user_counts = {}
        for log in failed_logs:
            user_key = f"{log.user_email} ({log.user_id})"
            user_counts[user_key] = user_counts.get(user_key, 0) + 1
        
        # Retornar itens acima do threshold
        suspicious = []
        
        for ip, count in ip_counts.items():
            if count >= threshold:
                suspicious.append({
                    "type": "ip",
                    "value": ip,
                    "count": count,
                    "threshold": threshold,
                })
        
        for user, count in user_counts.items():
            if count >= threshold:
                suspicious.append({
                    "type": "user",
                    "value": user,
                    "count": count,
                    "threshold": threshold,
                })
        
        return suspicious

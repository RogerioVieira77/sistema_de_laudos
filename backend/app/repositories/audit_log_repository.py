"""
AuditLog Repository
Acesso a dados de auditoria com queries otimizadas
Autor: Sistema de Laudos
Data: 2024-02-03
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models import AuditLog, AuditAction, AuditStatus


class AuditLogRepository:
    """
    Repository para operações em AuditLog
    Fornece métodos para query otimizadas de logs de auditoria
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
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
        Criar e salvar um novo registro de auditoria
        """
        audit_log = AuditLog.log_action(
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
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def get_by_id(self, audit_log_id: str) -> Optional[AuditLog]:
        """Buscar log por ID"""
        return self.db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()
    
    def get_by_user(
        self,
        user_id: str,
        limit: int = 100,
        skip: int = 0,
        days_back: int = 90,
    ) -> List[AuditLog]:
        """
        Buscar todos os logs de um usuário nos últimos N dias
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        return (
            self.db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.timestamp >= cutoff_date,
                )
            )
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
            .offset(skip)
            .all()
        )
    
    def get_by_tenant(
        self,
        tenant_id: str,
        limit: int = 100,
        skip: int = 0,
        days_back: int = 90,
        action: Optional[AuditAction] = None,
        status: Optional[AuditStatus] = None,
    ) -> List[AuditLog]:
        """
        Buscar todos os logs de um tenant (admin/compliance)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = self.db.query(AuditLog).filter(
            and_(
                AuditLog.tenant_id == tenant_id,
                AuditLog.timestamp >= cutoff_date,
            )
        )
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if status:
            query = query.filter(AuditLog.status == status)
        
        return (
            query
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
            .offset(skip)
            .all()
        )
    
    def get_by_resource(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 100,
        skip: int = 0,
    ) -> List[AuditLog]:
        """
        Buscar todos os logs relacionados a um recurso específico
        Útil para ver histórico de um contrato, parecer, etc
        """
        return (
            self.db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.resource_type == resource_type,
                    AuditLog.resource_id == resource_id,
                )
            )
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
            .offset(skip)
            .all()
        )
    
    def get_failed_actions(
        self,
        tenant_id: str,
        limit: int = 100,
        skip: int = 0,
        days_back: int = 30,
    ) -> List[AuditLog]:
        """
        Buscar ações que falharam (error ou blocked)
        Útil para detectar tentativas de segurança
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        return (
            self.db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.tenant_id == tenant_id,
                    AuditLog.timestamp >= cutoff_date,
                    AuditLog.status.in_([AuditStatus.ERROR, AuditStatus.BLOCKED]),
                )
            )
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
            .offset(skip)
            .all()
        )
    
    def get_by_ip_address(
        self,
        ip_address: str,
        limit: int = 100,
        skip: int = 0,
        days_back: int = 7,
    ) -> List[AuditLog]:
        """
        Buscar todas as ações de um IP
        Útil para detectar anomalias/ataques
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        return (
            self.db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.ip_address == ip_address,
                    AuditLog.timestamp >= cutoff_date,
                )
            )
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
            .offset(skip)
            .all()
        )
    
    def cleanup_old_logs(self, days_retention: int = 365) -> int:
        """
        Deletar logs com mais de N dias (para compliance/storage)
        Retorna quantidade de logs deletados
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_retention)
        
        deleted_count = (
            self.db.query(AuditLog)
            .filter(AuditLog.timestamp < cutoff_date)
            .delete()
        )
        
        self.db.commit()
        
        return deleted_count
    
    def get_activity_summary(
        self,
        tenant_id: str,
        days_back: int = 30,
    ) -> dict:
        """
        Obter resumo de atividades do tenant
        Retorna contagem por ação, status, etc
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        logs = (
            self.db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.tenant_id == tenant_id,
                    AuditLog.timestamp >= cutoff_date,
                )
            )
            .all()
        )
        
        # Contar por ação
        actions = {}
        statuses = {}
        resources = {}
        users = set()
        
        for log in logs:
            # Contar por ação
            action_name = log.action.value
            actions[action_name] = actions.get(action_name, 0) + 1
            
            # Contar por status
            status_name = log.status.value
            statuses[status_name] = statuses.get(status_name, 0) + 1
            
            # Contar por recurso
            resource_name = log.resource_type
            resources[resource_name] = resources.get(resource_name, 0) + 1
            
            # Contar usuários únicos
            if log.user_id:
                users.add(log.user_id)
        
        return {
            "total_actions": len(logs),
            "actions": actions,
            "statuses": statuses,
            "resources": resources,
            "unique_users": len(users),
            "date_range": {
                "from": cutoff_date.isoformat(),
                "to": datetime.utcnow().isoformat(),
            },
        }

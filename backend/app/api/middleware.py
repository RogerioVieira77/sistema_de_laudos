"""
Middleware de Auditoria
Registra todas as requisições para compliance e segurança
Autor: Sistema de Laudos
Data: 2024-02-03
"""

import json
import time
import logging
from datetime import datetime
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.orm import Session

from app.models import AuditLog, AuditAction, AuditStatus
from app.api.dependencies import get_db
from app.core.oidc_models import Identity

logger = logging.getLogger(__name__)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra todas as requisições para auditoria
    
    Responsável por:
    - Capturar metadados da requisição (método, path, IP, User-Agent)
    - Extrair identidade do usuário (JWT)
    - Registrar resultado (status code, erro)
    - Armazenar no banco de dados para compliance
    """
    
    # Endpoints que NÃO devem ser auditados (muitos logs)
    SKIP_AUDIT_PATHS = {
        "/api/v1/health",
        "/api/v1/docs",
        "/api/v1/openapi.json",
        "/api/v1/redoc",
    }
    
    # Mapeamento de métodos HTTP para ações de auditoria
    METHOD_TO_ACTION = {
        "POST": AuditAction.CREATE,
        "PUT": AuditAction.UPDATE,
        "PATCH": AuditAction.UPDATE,
        "DELETE": AuditAction.DELETE,
        "GET": AuditAction.READ,
        "HEAD": AuditAction.READ,
        "OPTIONS": AuditAction.READ,
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa a requisição e registra na auditoria
        """
        # Verificar se path deve ser auditado
        if any(request.url.path.startswith(skip) for skip in self.SKIP_AUDIT_PATHS):
            return await call_next(request)
        
        # Capturar metadados da requisição
        start_time = time.time()
        method = request.method
        path = request.url.path
        query_string = str(request.url.query) if request.url.query else ""
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")[:500]
        
        # Extrair identidade do JWT (se disponível)
        user_id: Optional[str] = None
        user_email: Optional[str] = None
        tenant_id: str = "default"
        
        try:
            # Tentar extrair do estado da requisição (se decorador foi aplicado)
            if hasattr(request.state, "identity"):
                identity: Identity = request.state.identity
                user_id = identity.sub
                user_email = identity.email
                tenant_id = identity.tenant_id
        except Exception as e:
            logger.warning(f"Erro ao extrair identidade: {e}")
        
        # Determinar tipo de recurso baseado no path
        resource_type = self._extract_resource_type(path)
        resource_id = self._extract_resource_id(path)
        
        # Determinar ação
        action = self.METHOD_TO_ACTION.get(method, AuditAction.READ)
        
        # Coletar parâmetros/detalhes adicionais
        details = {
            "method": method,
            "path": path,
            "query_string": query_string,
        }
        
        # Executar endpoint
        response: Response = None
        status_code = 500
        error_message = None
        audit_status = AuditStatus.SUCCESS
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Classificar status baseado no status code
            if status_code >= 400:
                audit_status = AuditStatus.ERROR
                details["error_status_code"] = status_code
                
                # Se foi bloqueado por segurança (401, 403)
                if status_code in (401, 403):
                    audit_status = AuditStatus.BLOCKED
        
        except Exception as e:
            # Capturar exceções durante o processamento
            status_code = 500
            audit_status = AuditStatus.ERROR
            error_message = str(e)[:500]
            logger.exception(f"Erro ao processar {method} {path}")
            raise
        
        finally:
            # Registrar na auditoria
            duration_ms = (time.time() - start_time) * 1000
            details["duration_ms"] = duration_ms
            details["status_code"] = status_code
            
            # Log assíncrono (não bloqueia a resposta)
            try:
                await self._log_audit(
                    user_id=user_id,
                    user_email=user_email,
                    tenant_id=tenant_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    status=audit_status,
                    error_message=error_message,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details=details,
                )
            except Exception as e:
                # Não falhar a requisição se logging falhar
                logger.error(f"Erro ao registrar auditoria: {e}", exc_info=True)
        
        return response
    
    async def _log_audit(
        self,
        user_id: Optional[str],
        user_email: Optional[str],
        tenant_id: str,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str],
        status: AuditStatus,
        error_message: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str],
        details: dict,
    ) -> None:
        """
        Registra a ação na auditoria (assincronamente)
        """
        try:
            # Usar a DB session separada para logging
            from app.models.database import SessionLocal
            db = SessionLocal()
            
            try:
                # Criar registro de auditoria
                audit_log = AuditLog.log_action(
                    user_id=user_id or "anonymous",
                    user_email=user_email or "unknown",
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
                
                # Salvar no banco
                db.add(audit_log)
                db.commit()
                
                logger.debug(
                    f"Auditoria registrada: {audit_log.user_email} "
                    f"{audit_log.action.value} {audit_log.resource_type}"
                )
            
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"Erro ao salvar auditoria: {e}", exc_info=True)
    
    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extrai o IP do cliente da requisição"""
        # Verificar X-Forwarded-For (proxy/load balancer)
        if "x-forwarded-for" in request.headers:
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Verificar X-Real-IP (nginx)
        if "x-real-ip" in request.headers:
            return request.headers["x-real-ip"]
        
        # Fallback para client
        if request.client:
            return request.client.host
        
        return "unknown"
    
    @staticmethod
    def _extract_resource_type(path: str) -> str:
        """
        Extrai o tipo de recurso do path
        
        Exemplos:
            /api/v1/contratos/123 -> contratos
            /api/v1/pareceres -> pareceres
            /api/v1/bureau/123 -> bureau
        """
        # Remover prefixo /api/v1/
        if path.startswith("/api/v1/"):
            path = path[8:]  # Remove "/api/v1/"
        
        # Remover leading slash
        if path.startswith("/"):
            path = path[1:]
        
        # Pegar primeira parte (resource type)
        parts = path.split("/")
        resource_type = parts[0] if parts else "unknown"
        
        return resource_type
    
    @staticmethod
    def _extract_resource_id(path: str) -> Optional[str]:
        """
        Extrai o ID do recurso do path
        
        Exemplos:
            /api/v1/contratos/123 -> 123
            /api/v1/pareceres/uuid-uuid -> uuid-uuid
            /api/v1/bureau -> None
        """
        # Remover prefixo /api/v1/
        if path.startswith("/api/v1/"):
            path = path[8:]
        
        # Remover leading slash
        if path.startswith("/"):
            path = path[1:]
        
        # Pegar partes do path
        parts = path.split("/")
        
        # Se tem pelo menos 2 partes e a segunda é numérica ou UUID
        if len(parts) >= 2:
            potential_id = parts[1]
            # Verificar se é um ID (não é uma sub-rota)
            if potential_id and not potential_id.isalpha():
                return potential_id
        
        return None

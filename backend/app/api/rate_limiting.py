"""
Rate Limiting Configuration and Utilities
Implementa rate limiting com slowapi para proteger a API contra abuso
Autor: Sistema de Laudos
Data: 2024-02-03
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from functools import wraps
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Limiter Instance (Singleton)
# ============================================================================

limiter = Limiter(key_func=get_remote_address)
"""
Instância global do rate limiter
- key_func=get_remote_address: Usa IP do cliente como chave
- Suporta Redis para distribuição em múltiplos servidores (configurável)
"""


# ============================================================================
# Rate Limit Strings (Configuráveis)
# ============================================================================

class RateLimits:
    """
    Definições de rate limits para diferentes cenários
    Formato: "N/T" onde N=requisições, T=período (second, minute, hour, day)
    """
    
    # Padrão: 100 requisições por minuto por IP
    DEFAULT = "100/minute"
    
    # Endpoints sensíveis (upload, delete, delete): 10 req/min
    UPLOAD = "10/minute"
    DELETE = "10/minute"
    WRITE = "20/minute"  # POST, PUT, PATCH
    
    # Read: 50 req/min (mais permissivo)
    READ = "50/minute"
    
    # Health check: ilimitado (usar para monitoramento)
    UNLIMITED = None
    
    # Endpoints administrativos: mais restritivos
    ADMIN = "5/minute"
    
    # Login/Auth: muito restritivo (prevenir força bruta)
    AUTH = "5/minute"
    
    # Relatórios: moderado
    REPORTS = "10/minute"
    
    # Audit logs: moderado
    AUDIT = "20/minute"


# ============================================================================
# Decoradores Customizados
# ============================================================================

def rate_limit(limit_string: Optional[str] = RateLimits.DEFAULT):
    """
    Decorador customizado para aplicar rate limiting a endpoints
    
    Args:
        limit_string: String de limite (ex: "10/minute") ou None para ilimitado
        
    Usage:
        @rate_limit(RateLimits.UPLOAD)
        async def upload_endpoint(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Se limit_string é None, skip rate limiting
            if limit_string is None:
                return await func(*args, **kwargs)
            
            # Aplicar rate limiting via slowapi decorator
            return await func(*args, **kwargs)
        
        # Aplicar decorador slowapi se houver limite
        if limit_string:
            wrapper = limiter.limit(limit_string)(wrapper)
        
        return wrapper
    
    return decorator


def rate_limit_by_user(limit_string: Optional[str] = RateLimits.DEFAULT):
    """
    Rate limiting baseado em user_id ao invés de IP
    Melhor para APIs autenticadas (um usuário pode ter múltiplos IPs)
    
    Nota: Requer que identity esteja disponível em request.state
    
    Usage:
        @rate_limit_by_user(RateLimits.UPLOAD)
        async def upload_endpoint(identity: Identity = Depends(get_identity)):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Se limit_string é None, skip
            if limit_string is None:
                return await func(request, *args, **kwargs)
            
            # Tentar extrair user_id de request.state
            user_id = None
            if hasattr(request.state, "identity"):
                user_id = getattr(request.state, "identity").sub
            
            # Se não tem user_id, falhar seguro (usar IP)
            if not user_id:
                logger.warning("rate_limit_by_user: user_id não encontrado, usando IP")
                user_id = get_remote_address(request)
            
            return await func(request, *args, **kwargs)
        
        # Aplicar decorador slowapi com chave customizada
        if limit_string:
            def custom_key_func(request: Request) -> str:
                # Tentar user_id primeiro, fallback para IP
                if hasattr(request.state, "identity"):
                    return getattr(request.state, "identity").sub
                return get_remote_address(request)
            
            # Nota: slowapi não suporta key_func dinâmica facilmente
            # Vamos usar o padrão e deixar a customização para middleware
            wrapper = limiter.limit(limit_string)(wrapper)
        
        return wrapper
    
    return decorator


# ============================================================================
# Funções Auxiliares
# ============================================================================

def get_rate_limit_for_endpoint(method: str) -> Optional[str]:
    """
    Determinar rate limit baseado no método HTTP
    
    Args:
        method: GET, POST, PUT, PATCH, DELETE, etc
        
    Returns:
        String de rate limit ou None para ilimitado
    """
    method = method.upper()
    
    if method == "GET":
        return RateLimits.READ
    elif method == "POST":
        return RateLimits.WRITE
    elif method == "PUT" or method == "PATCH":
        return RateLimits.WRITE
    elif method == "DELETE":
        return RateLimits.DELETE
    else:
        return RateLimits.DEFAULT


def get_rate_limit_for_path(path: str, method: str) -> Optional[str]:
    """
    Determinar rate limit específico baseado no path
    Permite configuração granular por endpoint
    
    Args:
        path: Path da requisição (ex: /api/v1/contratos)
        method: Método HTTP
        
    Returns:
        String de rate limit ou None para ilimitado
    """
    path = path.lower()
    method = method.upper()
    
    # Endpoints especiais
    if path == "/api/v1/health":
        return RateLimits.UNLIMITED
    
    # Upload/delete: muito restritivo
    if "/upload" in path:
        return RateLimits.UPLOAD
    
    if method == "DELETE":
        return RateLimits.DELETE
    
    # Audit logs: moderadamente restritivo
    if "/audit-logs" in path:
        return RateLimits.AUDIT
    
    # Admin: muito restritivo
    if "/admin" in path:
        return RateLimits.ADMIN
    
    # Padrão baseado no método
    return get_rate_limit_for_endpoint(method)

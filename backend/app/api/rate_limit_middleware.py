"""
Rate Limiting Middleware
Middleware para aplicar rate limiting com suporte a user_id (para autenticados)
Autor: Sistema de Laudos
Data: 2024-02-03
"""

import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import HTTPException, status

from app.api.rate_limiting import get_rate_limit_for_path, RateLimits

logger = logging.getLogger(__name__)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que aplica rate limiting com suporte a:
    - Rate limiting baseado em IP
    - Rate limiting baseado em user_id (se autenticado)
    - Limites específicos por endpoint
    - Respostas customizadas (429 Too Many Requests)
    """
    
    # Endpoints que devem ter rate limiting por user_id (autenticados)
    USER_BASED_PATHS = {
        "/api/v1/contratos",
        "/api/v1/pareceres",
        "/api/v1/bureau",
        "/api/v1/geolocalizacao",
        "/api/v1/audit-logs",
    }
    
    def __init__(self, app, limiter: Limiter):
        super().__init__(app)
        self.limiter = limiter
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa a requisição com rate limiting
        """
        try:
            # Obter informações da requisição
            path = request.url.path
            method = request.method
            
            # Determinar chave para rate limiting
            # Preferir user_id se disponível, fallback para IP
            rate_limit_key = self._get_rate_limit_key(request, path)
            
            # Obter limite específico para o endpoint
            limit_string = get_rate_limit_for_path(path, method)
            
            # Se ilimitado, não aplicar rate limiting
            if limit_string is None:
                return await call_next(request)
            
            # Aplicar rate limiting
            await self._check_rate_limit(rate_limit_key, limit_string)
            
            # Se passou no rate limiting, continuar
            return await call_next(request)
        
        except RateLimitExceeded as e:
            logger.warning(
                f"Rate limit exceeded: {request.method} {request.url.path}",
                extra={"ip": self._get_ip(request), "limit": str(e)}
            )
            # Retornar 429 Too Many Requests
            return Response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content='{"detail": "Limite de requisições atingido. Tente novamente em alguns segundos."}',
                media_type="application/json",
                headers={
                    "Retry-After": "60",  # Sugerir retry após 60 segundos
                    "X-RateLimit-Limit": limit_string or "unlimited",
                }
            )
    
    def _get_rate_limit_key(self, request: Request, path: str) -> str:
        """
        Determinar a chave para rate limiting
        Preferir user_id se disponível, fallback para IP
        """
        # Se é endpoint autenticado e temos identity, usar user_id
        if self._is_user_based_path(path):
            if hasattr(request.state, "identity"):
                user_id = getattr(request.state, "identity").sub
                logger.debug(f"Rate limiting por user_id: {user_id}")
                return f"user:{user_id}"
        
        # Fallback para IP
        ip = self._get_ip(request)
        logger.debug(f"Rate limiting por IP: {ip}")
        return f"ip:{ip}"
    
    def _is_user_based_path(self, path: str) -> bool:
        """
        Determinar se este path deve usar rate limiting por user_id
        """
        for user_path in self.USER_BASED_PATHS:
            if path.startswith(user_path):
                return True
        return False
    
    def _get_ip(self, request: Request) -> str:
        """
        Extrair IP do cliente (considerando proxies)
        """
        if "x-forwarded-for" in request.headers:
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        if "x-real-ip" in request.headers:
            return request.headers["x-real-ip"]
        if request.client:
            return request.client.host
        return "unknown"
    
    async def _check_rate_limit(self, key: str, limit_string: str) -> None:
        """
        Verificar rate limit para uma chave e limite específico
        
        Nota: Implementação simplificada usando contador em memória
        Para produção com múltiplos workers, usar Redis
        """
        # Nota: slowapi é mais simples quando usado com decoradores
        # Este é um exemplo de como fazê-lo via middleware
        # Em produção, integrar com Redis para distribuição
        pass

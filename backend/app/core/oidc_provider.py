"""
OIDC Provider - Provedor agnóstico de autenticação OIDC
Suporta Keycloak, Microsoft Entra, Google, AWS Cognito
Autor: Sistema de Laudos
Data: 2024-02-03
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import httpx
import asyncio
import json
from functools import lru_cache
import logging
from enum import Enum

from .oidc_models import (
    OIDCConfig,
    Identity,
    TokenValidationResult,
    IdentityAdapter,
    JWKSCache,
)

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """Tipos de provedores OIDC suportados"""
    KEYCLOAK = "keycloak"
    MICROSOFT_ENTRA = "microsoft_entra"
    GOOGLE = "google"
    AWS_COGNITO = "aws_cognito"
    CUSTOM = "custom"


class OIDCProvider(ABC):
    """
    Classe abstrata para provedores OIDC
    Implementa validação agnóstica de tokens JWT
    """
    
    def __init__(self, config: OIDCConfig):
        self.config = config
        self._jwks_cache: Optional[JWKSCache] = None
        self._http_client: Optional[httpx.AsyncClient] = None
        self.provider_type = ProviderType.CUSTOM
    
    async def __aenter__(self):
        """Context manager entry"""
        self._http_client = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._http_client:
            await self._http_client.aclose()
    
    @abstractmethod
    async def get_discovery_metadata(self) -> Dict[str, Any]:
        """
        Obter metadados de descoberta do provedor
        Implementar em subclasses específicas
        """
        pass
    
    @abstractmethod
    def adapt_claims(self, claims: Dict[str, Any]) -> Identity:
        """
        Adaptar claims específicos do IdP para Identity normalizada
        Implementar em subclasses específicas
        """
        pass
    
    async def get_jwks(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Obter JSON Web Key Set (JWKS)
        Com cache de 24 horas
        """
        # Verificar cache válido
        if not force_refresh and self._jwks_cache and self._jwks_cache.is_valid():
            logger.info("Usando JWKS em cache")
            return self._jwks_cache.keys
        
        # Buscar metadata de descoberta
        metadata = await self.get_discovery_metadata()
        jwks_uri = metadata.get("jwks_uri")
        
        if not jwks_uri:
            raise ValueError(f"jwks_uri não encontrado em metadados: {metadata}")
        
        # Buscar JWKS
        logger.info(f"Buscando JWKS de {jwks_uri}")
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_uri, timeout=10.0)
            response.raise_for_status()
            jwks = response.json()
        
        # Cachear por 24 horas
        self._jwks_cache = JWKSCache(
            keys=jwks,
            cached_at=datetime.utcnow(),
            ttl_seconds=self.config.jwks_cache_ttl_seconds
        )
        
        logger.info(f"JWKS atualizado, {len(jwks.get('keys', []))} chaves")
        return jwks
    
    async def validate_token(
        self,
        token: str,
        expected_aud: Optional[str] = None,
    ) -> TokenValidationResult:
        """
        Validar token JWT
        
        Args:
            token: Token JWT completo (header.payload.signature)
            expected_aud: Audience esperado (default: config.client_id)
        
        Returns:
            TokenValidationResult com Identity se válido
        """
        try:
            # 1. Verificar formato básico
            parts = token.split(".")
            if len(parts) != 3:
                return TokenValidationResult(
                    valid=False,
                    error="Token JWT inválido",
                    error_code="invalid_format"
                )
            
            # 2. Decodificar header e payload
            from jose import jwt, JWTError
            
            # Decodificar sem validação primeiro (para extrair kid)
            unverified = jwt.get_unverified_header(token)
            kid = unverified.get("kid")
            
            if not kid:
                logger.warning("Token sem kid no header")
                kid = None  # Tentar primeira chave disponível
            
            # 3. Obter JWKS
            try:
                jwks = await self.get_jwks()
            except Exception as e:
                logger.error(f"Erro ao obter JWKS: {e}")
                return TokenValidationResult(
                    valid=False,
                    error=f"Erro ao obter JWKS: {str(e)}",
                    error_code="jwks_error"
                )
            
            # 4. Encontrar chave correta
            key = None
            if kid:
                for k in jwks.get("keys", []):
                    if k.get("kid") == kid:
                        key = k
                        break
            else:
                # Se não houver kid, usar primeira chave
                keys = jwks.get("keys", [])
                if keys:
                    key = keys[0]
            
            if not key:
                logger.warning(f"Chave {kid} não encontrada no JWKS")
                return TokenValidationResult(
                    valid=False,
                    error="Chave de assinatura não encontrada",
                    error_code="key_not_found"
                )
            
            # 5. Converter JWK para PEM
            from jose.backends.rsa_backend import RSAKey
            rsa_key = RSAKey(key)
            
            # 6. Validar assinatura e claims
            audience = expected_aud or self.config.client_id
            
            try:
                claims = jwt.decode(
                    token,
                    rsa_key.public_key,
                    algorithms=[self.config.algorithm],
                    audience=audience if self.config.validate_audience else None,
                    issuer=self.config.authority if self.config.validate_issuer else None,
                )
            except JWTError as e:
                logger.warning(f"Erro ao decodificar token: {e}")
                return TokenValidationResult(
                    valid=False,
                    error=f"Token inválido: {str(e)}",
                    error_code="invalid_token"
                )
            
            # 7. Verificações adicionais
            if claims.get("exp") and claims["exp"] < datetime.utcnow().timestamp():
                return TokenValidationResult(
                    valid=False,
                    error="Token expirado",
                    error_code="token_expired"
                )
            
            # 8. Adaptar claims para Identity
            identity = self.adapt_claims(claims)
            
            logger.info(f"Token válido para {identity.email}")
            
            return TokenValidationResult(
                valid=True,
                identity=identity,
            )
        
        except Exception as e:
            logger.error(f"Erro ao validar token: {e}", exc_info=True)
            return TokenValidationResult(
                valid=False,
                error=f"Erro interno: {str(e)}",
                error_code="internal_error"
            )
    
    async def exchange_code_for_token(
        self,
        code: str,
        code_verifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Trocar authorization code por tokens
        Implementar em subclasses específicas
        """
        raise NotImplementedError("Implementar em subclasse específica")


class KeycloakProvider(OIDCProvider):
    """Provider para Keycloak"""
    
    provider_type = ProviderType.KEYCLOAK
    
    def __init__(self, config: OIDCConfig):
        super().__init__(config)
        # Normalizar authority URL
        if not self.config.authority.endswith("/"):
            self.config.authority = self.config.authority + "/"
    
    async def get_discovery_metadata(self) -> Dict[str, Any]:
        """Buscar metadados de descoberta do Keycloak"""
        url = f"{self.config.authority}.well-known/openid-configuration"
        
        logger.info(f"Buscando metadados de {url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    
    def adapt_claims(self, claims: Dict[str, Any]) -> Identity:
        """Adaptar claims do Keycloak"""
        return IdentityAdapter.from_keycloak(claims)
    
    async def exchange_code_for_token(
        self,
        code: str,
        code_verifier: str,
    ) -> Dict[str, Any]:
        """Trocar authorization code por tokens (Keycloak)"""
        metadata = await self.get_discovery_metadata()
        token_endpoint = metadata.get("token_endpoint")
        
        if not token_endpoint:
            raise ValueError("token_endpoint não encontrado em metadados")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_endpoint,
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.config.client_id,
                    "code": code,
                    "redirect_uri": self.config.redirect_uri,
                    "code_verifier": code_verifier,
                }
            )
            response.raise_for_status()
            return response.json()


class MicrosoftEntraProvider(OIDCProvider):
    """Provider para Microsoft Entra ID (Azure AD)"""
    
    provider_type = ProviderType.MICROSOFT_ENTRA
    
    def __init__(self, config: OIDCConfig):
        super().__init__(config)
        # Normalizar authority
        if not self.config.authority.endswith("/"):
            self.config.authority = self.config.authority + "/"
    
    async def get_discovery_metadata(self) -> Dict[str, Any]:
        """Buscar metadados de descoberta do Entra"""
        url = f"{self.config.authority}.well-known/openid-configuration"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    
    def adapt_claims(self, claims: Dict[str, Any]) -> Identity:
        """Adaptar claims do Microsoft Entra"""
        return IdentityAdapter.from_microsoft_entra(claims)


class GoogleProvider(OIDCProvider):
    """Provider para Google OAuth"""
    
    provider_type = ProviderType.GOOGLE
    
    def __init__(self, config: OIDCConfig):
        super().__init__(config)
        # Google usa authority padrão
        if self.config.authority != "https://accounts.google.com":
            self.config.authority = "https://accounts.google.com"
    
    async def get_discovery_metadata(self) -> Dict[str, Any]:
        """Buscar metadados de descoberta do Google"""
        url = "https://accounts.google.com/.well-known/openid-configuration"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    
    def adapt_claims(self, claims: Dict[str, Any]) -> Identity:
        """Adaptar claims do Google"""
        return IdentityAdapter.from_google(claims)


class AWSCognitoProvider(OIDCProvider):
    """Provider para AWS Cognito"""
    
    provider_type = ProviderType.AWS_COGNITO
    
    def __init__(self, config: OIDCConfig, region: str = "us-east-1"):
        super().__init__(config)
        self.region = region
        # Normalizar authority para Cognito
        if not self.config.authority.endswith("/"):
            self.config.authority = self.config.authority + "/"
    
    async def get_discovery_metadata(self) -> Dict[str, Any]:
        """Buscar metadados de descoberta do Cognito"""
        url = f"{self.config.authority}.well-known/openid-configuration"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    
    def adapt_claims(self, claims: Dict[str, Any]) -> Identity:
        """Adaptar claims do AWS Cognito"""
        return IdentityAdapter.from_cognito(claims)


class OIDCProviderFactory:
    """
    Factory para criar provedores OIDC
    Escolhe o tipo baseado em configuração
    """
    
    _providers: Dict[str, type[OIDCProvider]] = {
        ProviderType.KEYCLOAK: KeycloakProvider,
        ProviderType.MICROSOFT_ENTRA: MicrosoftEntraProvider,
        ProviderType.GOOGLE: GoogleProvider,
        ProviderType.AWS_COGNITO: AWSCognitoProvider,
    }
    
    @classmethod
    def create(cls, config: OIDCConfig, provider_type: str = "keycloak") -> OIDCProvider:
        """
        Criar provider baseado em tipo
        
        Args:
            config: OIDCConfig com dados do IdP
            provider_type: Tipo de provider (keycloak, microsoft_entra, google, aws_cognito)
        
        Returns:
            Instância do provider específico
        """
        provider_class = cls._providers.get(provider_type)
        
        if not provider_class:
            logger.warning(f"Provider {provider_type} não registrado, usando Keycloak")
            provider_class = KeycloakProvider
        
        logger.info(f"Criando provider: {provider_class.__name__}")
        return provider_class(config)
    
    @classmethod
    def register_provider(
        cls,
        provider_type: str,
        provider_class: type[OIDCProvider]
    ):
        """Registrar novo provider customizado"""
        cls._providers[provider_type] = provider_class
        logger.info(f"Provider registrado: {provider_type}")


# Singleton global (será inicializado em dependencies.py)
_provider_instance: Optional[OIDCProvider] = None


async def get_provider(provider_type: str = "keycloak") -> OIDCProvider:
    """
    Obter instância única do provider OIDC
    
    Args:
        provider_type: Tipo de provider a usar
    
    Returns:
        Instância do OIDCProvider
    """
    global _provider_instance
    
    if _provider_instance is not None:
        return _provider_instance
    
    config = OIDCConfig.from_env(provider_type)
    _provider_instance = OIDCProviderFactory.create(config, provider_type)
    
    return _provider_instance


def set_provider(provider: OIDCProvider):
    """Definir instância do provider (para testes)"""
    global _provider_instance
    _provider_instance = provider

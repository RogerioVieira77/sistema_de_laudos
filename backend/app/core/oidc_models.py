"""
OIDC Models - Modelos de configuração e identidade agnósticos de IdP
Autor: Sistema de Laudos
Data: 2024-02-03
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json


@dataclass
class OIDCConfig:
    """Configuração agnóstica para qualquer provedor OIDC"""
    
    # Endpoints obrigatórios
    authority: str  # https://idp.company.com/realms/sistema-laudos
    client_id: str  # sistema-laudos-web ou sistema-laudos-api
    client_secret: Optional[str] = None  # Only for confidential clients
    
    # URLs de redirecionamento
    redirect_uri: str = "http://localhost:5173/callback"
    silent_redirect_uri: str = "http://localhost:5173/silent-renew.html"
    
    # Escopos e configurações de token
    scope: str = "openid profile email roles"
    response_type: str = "code"  # Authorization Code Flow
    
    # Cache JWKS
    jwks_cache_ttl_seconds: int = 86400  # 24 horas
    
    # Token validation
    validate_issuer: bool = True
    validate_audience: bool = True
    algorithm: str = "RS256"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return asdict(self)
    
    @classmethod
    def from_env(cls, provider_type: str = "keycloak") -> "OIDCConfig":
        """Criar configuração a partir de variáveis de ambiente"""
        import os
        
        authority = os.getenv("OIDC_AUTHORITY")
        if not authority:
            raise ValueError("OIDC_AUTHORITY environment variable not set")
        
        return cls(
            authority=authority,
            client_id=os.getenv("OIDC_CLIENT_ID", f"sistema-laudos-{provider_type}"),
            client_secret=os.getenv("OIDC_CLIENT_SECRET"),
            redirect_uri=os.getenv(
                "OIDC_REDIRECT_URI", 
                "http://localhost:5173/callback"
            ),
            silent_redirect_uri=os.getenv(
                "OIDC_SILENT_REDIRECT_URI",
                "http://localhost:5173/silent-renew.html"
            ),
        )


@dataclass
class JWKSCache:
    """Cache para JWKS com TTL"""
    
    keys: Dict[str, Any]
    cached_at: datetime
    ttl_seconds: int = 86400  # 24 horas
    
    def is_valid(self) -> bool:
        """Verificar se o cache ainda é válido"""
        expires_at = self.cached_at + timedelta(seconds=self.ttl_seconds)
        return datetime.utcnow() < expires_at
    
    def get_key(self, kid: str) -> Optional[Dict[str, Any]]:
        """Obter chave específica do cache"""
        if not self.is_valid():
            return None
        
        # Procurar chave por kid
        for key in self.keys.get("keys", []):
            if key.get("kid") == kid:
                return key
        
        return None


@dataclass
class Identity:
    """
    Identidade normalizada do usuário
    Agnóstica a qualquer IdP (Keycloak, Entra, Google, Cognito)
    """
    
    # Identificadores
    sub: str  # Subject (user ID único)
    email: str
    preferred_username: str
    
    # Contexto e autorização
    roles: List[str] = field(default_factory=list)
    tenant_id: str = field(default="default")  # Para multi-tenancy
    
    # Claims originais do JWT
    raw_claims: Dict[str, Any] = field(default_factory=dict)
    
    # Validação de token
    iss: str = ""  # Issuer
    aud: str = ""  # Audience
    exp: int = 0  # Expiration time
    iat: int = 0  # Issued at
    
    # Informações opcionais
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    phone_number: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário (excluindo raw_claims)"""
        return {
            "sub": self.sub,
            "email": self.email,
            "preferred_username": self.preferred_username,
            "roles": self.roles,
            "tenant_id": self.tenant_id,
            "iss": self.iss,
            "aud": self.aud,
            "exp": self.exp,
            "iat": self.iat,
            "name": self.name,
        }
    
    def has_role(self, *roles: str) -> bool:
        """Verificar se possui uma ou mais roles"""
        return any(role in self.roles for role in roles)
    
    def is_admin(self) -> bool:
        """Atalho para verificar se é admin"""
        return self.has_role("admin")
    
    def is_expired(self) -> bool:
        """Verificar se token expirou"""
        from datetime import datetime
        return datetime.utcfromtimestamp(self.exp) < datetime.utcnow()
    
    def __str__(self) -> str:
        return f"Identity(sub={self.sub}, email={self.email}, roles={self.roles})"
    
    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class TokenValidationResult:
    """Resultado da validação de um token"""
    
    valid: bool
    identity: Optional[Identity] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    
    def __bool__(self) -> bool:
        """Permitir usar resultado como boolean"""
        return self.valid


class IdentityAdapter:
    """
    Adaptador para normalizar claims de diferentes IdPs
    
    Mapeia claims específicos de cada IdP para a estrutura Identity padrão
    """
    
    @staticmethod
    def from_keycloak(claims: Dict[str, Any]) -> Identity:
        """Adaptar claims do Keycloak para Identity"""
        return Identity(
            sub=claims.get("sub", ""),
            email=claims.get("email", ""),
            preferred_username=claims.get("preferred_username", ""),
            roles=claims.get("roles", []),
            tenant_id=claims.get("tenant_id", "default"),
            raw_claims=claims,
            iss=claims.get("iss", ""),
            aud=claims.get("aud", ""),
            exp=claims.get("exp", 0),
            iat=claims.get("iat", 0),
            name=claims.get("name"),
            given_name=claims.get("given_name"),
            family_name=claims.get("family_name"),
            phone_number=claims.get("phone_number"),
        )
    
    @staticmethod
    def from_microsoft_entra(claims: Dict[str, Any]) -> Identity:
        """Adaptar claims do Microsoft Entra ID"""
        # Microsoft usa 'oid' como subject
        return Identity(
            sub=claims.get("oid", claims.get("sub", "")),
            email=claims.get("upn", claims.get("email", "")),
            preferred_username=claims.get("preferred_username", claims.get("upn", "")),
            # Microsoft mapeia roles em 'roles' claim se configurado
            roles=claims.get("roles", claims.get("appid", []) if isinstance(claims.get("appid"), list) else []),
            tenant_id=claims.get("tid", "default"),  # Azure tenant ID
            raw_claims=claims,
            iss=claims.get("iss", ""),
            aud=claims.get("aud", ""),
            exp=claims.get("exp", 0),
            iat=claims.get("iat", 0),
            name=claims.get("name"),
            given_name=claims.get("given_name"),
            family_name=claims.get("family_name"),
        )
    
    @staticmethod
    def from_google(claims: Dict[str, Any]) -> Identity:
        """Adaptar claims do Google OAuth"""
        return Identity(
            sub=claims.get("sub", ""),
            email=claims.get("email", ""),
            preferred_username=claims.get("email", "").split("@")[0],
            roles=[],  # Google não mapeia roles por padrão
            tenant_id="google",  # Marcar como Google
            raw_claims=claims,
            iss=claims.get("iss", ""),
            aud=claims.get("aud", ""),
            exp=claims.get("exp", 0),
            iat=claims.get("iat", 0),
            name=claims.get("name"),
            given_name=claims.get("given_name"),
            family_name=claims.get("family_name"),
        )
    
    @staticmethod
    def from_cognito(claims: Dict[str, Any]) -> Identity:
        """Adaptar claims do AWS Cognito"""
        return Identity(
            sub=claims.get("sub", ""),
            email=claims.get("email", ""),
            preferred_username=claims.get("cognito:username", claims.get("email", "")),
            # Cognito mapeia grupos em 'cognito:groups'
            roles=claims.get("cognito:groups", []),
            tenant_id=claims.get("custom:tenant_id", "default"),
            raw_claims=claims,
            iss=claims.get("iss", ""),
            aud=claims.get("aud", ""),
            exp=claims.get("exp", 0),
            iat=claims.get("iat", 0),
            name=claims.get("name"),
            given_name=claims.get("given_name"),
            family_name=claims.get("family_name"),
        )

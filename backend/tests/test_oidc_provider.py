"""
Testes unitários para OIDC Provider
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json

from app.core import (
    OIDCConfig,
    Identity,
    KeycloakProvider,
    MicrosoftEntraProvider,
    GoogleProvider,
    OIDCProviderFactory,
    IdentityAdapter,
    TokenValidationResult,
)


@pytest.fixture
def keycloak_config():
    """Configuração de teste para Keycloak"""
    return OIDCConfig(
        authority="https://keycloak.example.com/realms/sistema-laudos",
        client_id="sistema-laudos-web",
        client_secret=None,
        redirect_uri="http://localhost:5173/callback",
    )


@pytest.fixture
def keycloak_provider(keycloak_config):
    """Provider Keycloak para testes"""
    return KeycloakProvider(keycloak_config)


@pytest.fixture
def sample_claims():
    """Claims de amostra de um token JWT válido"""
    now = datetime.utcnow()
    return {
        "sub": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "preferred_username": "johndoe",
        "roles": ["analista", "revisor"],
        "tenant_id": "tenant-123",
        "iss": "https://keycloak.example.com/realms/sistema-laudos",
        "aud": "sistema-laudos-web",
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "iat": int(now.timestamp()),
        "name": "John Doe",
    }


class TestOIDCConfig:
    """Testes para OIDCConfig"""
    
    def test_create_config(self, keycloak_config):
        """Testar criação de configuração"""
        assert keycloak_config.authority
        assert keycloak_config.client_id == "sistema-laudos-web"
        assert keycloak_config.scope == "openid profile email roles"
    
    def test_config_to_dict(self, keycloak_config):
        """Testar conversão para dicionário"""
        config_dict = keycloak_config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict["client_id"] == "sistema-laudos-web"
    
    @patch.dict("os.environ", {
        "OIDC_AUTHORITY": "https://auth.example.com",
        "OIDC_CLIENT_ID": "test-client",
    })
    def test_config_from_env(self):
        """Testar carregamento de configuração de variáveis de ambiente"""
        config = OIDCConfig.from_env()
        assert config.authority == "https://auth.example.com"
        assert config.client_id == "test-client"


class TestIdentity:
    """Testes para classe Identity"""
    
    def test_create_identity(self, sample_claims):
        """Testar criação de identidade"""
        identity = Identity(
            sub=sample_claims["sub"],
            email=sample_claims["email"],
            preferred_username=sample_claims["preferred_username"],
            roles=sample_claims["roles"],
            tenant_id=sample_claims["tenant_id"],
        )
        
        assert identity.email == "user@example.com"
        assert "analista" in identity.roles
        assert identity.tenant_id == "tenant-123"
    
    def test_identity_has_role(self, sample_claims):
        """Testar verificação de roles"""
        identity = Identity(
            sub=sample_claims["sub"],
            email=sample_claims["email"],
            preferred_username=sample_claims["preferred_username"],
            roles=sample_claims["roles"],
        )
        
        assert identity.has_role("analista")
        assert identity.has_role("revisor")
        assert not identity.has_role("admin")
    
    def test_identity_is_admin(self):
        """Testar verificação de admin"""
        admin_identity = Identity(
            sub="123",
            email="admin@example.com",
            preferred_username="admin",
            roles=["admin"],
        )
        
        assert admin_identity.is_admin()
        
        user_identity = Identity(
            sub="456",
            email="user@example.com",
            preferred_username="user",
            roles=["analista"],
        )
        
        assert not user_identity.is_admin()
    
    def test_identity_to_dict(self, sample_claims):
        """Testar conversão para dicionário"""
        identity = IdentityAdapter.from_keycloak(sample_claims)
        identity_dict = identity.to_dict()
        
        assert identity_dict["email"] == "user@example.com"
        assert identity_dict["roles"] == ["analista", "revisor"]
        assert "raw_claims" not in identity_dict


class TestIdentityAdapter:
    """Testes para adaptador de claims"""
    
    def test_adapt_keycloak_claims(self, sample_claims):
        """Testar adaptação de claims do Keycloak"""
        identity = IdentityAdapter.from_keycloak(sample_claims)
        
        assert identity.sub == sample_claims["sub"]
        assert identity.email == sample_claims["email"]
        assert identity.roles == sample_claims["roles"]
        assert identity.tenant_id == sample_claims["tenant_id"]
    
    def test_adapt_microsoft_entra_claims(self):
        """Testar adaptação de claims do Microsoft Entra"""
        claims = {
            "oid": "550e8400-e29b-41d4-a716-446655440000",
            "upn": "user@company.onmicrosoft.com",
            "name": "John Doe",
            "tid": "tenant-123",
            "roles": ["admin"],
        }
        
        identity = IdentityAdapter.from_microsoft_entra(claims)
        
        assert identity.sub == claims["oid"]
        assert identity.email == claims["upn"]
        assert identity.roles == claims["roles"]
    
    def test_adapt_google_claims(self):
        """Testar adaptação de claims do Google"""
        claims = {
            "sub": "google-id-123",
            "email": "user@gmail.com",
            "name": "John Doe",
            "email_verified": True,
        }
        
        identity = IdentityAdapter.from_google(claims)
        
        assert identity.sub == claims["sub"]
        assert identity.email == claims["email"]
        assert identity.tenant_id == "google"
    
    def test_adapt_cognito_claims(self):
        """Testar adaptação de claims do AWS Cognito"""
        claims = {
            "sub": "cognito-id-123",
            "email": "user@example.com",
            "cognito:username": "johndoe",
            "cognito:groups": ["admins"],
            "custom:tenant_id": "aws-tenant",
        }
        
        identity = IdentityAdapter.from_cognito(claims)
        
        assert identity.sub == claims["sub"]
        assert identity.email == claims["email"]
        assert identity.preferred_username == "johndoe"
        assert identity.roles == ["admins"]


class TestTokenValidationResult:
    """Testes para TokenValidationResult"""
    
    def test_valid_result(self, sample_claims):
        """Testar resultado válido"""
        identity = IdentityAdapter.from_keycloak(sample_claims)
        result = TokenValidationResult(valid=True, identity=identity)
        
        assert result.valid
        assert result.identity.email == "user@example.com"
        assert not result.error
    
    def test_invalid_result(self):
        """Testar resultado inválido"""
        result = TokenValidationResult(
            valid=False,
            error="Token inválido",
            error_code="invalid_signature"
        )
        
        assert not result.valid
        assert result.error == "Token inválido"
        assert result.error_code == "invalid_signature"
    
    def test_result_as_bool(self, sample_claims):
        """Testar uso de resultado como boolean"""
        identity = IdentityAdapter.from_keycloak(sample_claims)
        valid_result = TokenValidationResult(valid=True, identity=identity)
        invalid_result = TokenValidationResult(valid=False, error="Error")
        
        assert bool(valid_result) is True
        assert bool(invalid_result) is False


class TestOIDCProviderFactory:
    """Testes para factory de providers"""
    
    def test_create_keycloak_provider(self, keycloak_config):
        """Testar criação de provider Keycloak"""
        provider = OIDCProviderFactory.create(keycloak_config, "keycloak")
        
        assert isinstance(provider, KeycloakProvider)
        assert provider.provider_type == "keycloak"
    
    def test_create_entra_provider(self, keycloak_config):
        """Testar criação de provider Microsoft Entra"""
        provider = OIDCProviderFactory.create(keycloak_config, "microsoft_entra")
        
        assert isinstance(provider, MicrosoftEntraProvider)
        assert provider.provider_type == "microsoft_entra"
    
    def test_create_google_provider(self, keycloak_config):
        """Testar criação de provider Google"""
        provider = OIDCProviderFactory.create(keycloak_config, "google")
        
        assert isinstance(provider, GoogleProvider)
        assert provider.provider_type == "google"
    
    def test_invalid_provider_type_defaults_to_keycloak(self, keycloak_config):
        """Testar que tipo inválido padrão para Keycloak"""
        provider = OIDCProviderFactory.create(keycloak_config, "invalid_provider")
        
        # Deve usar Keycloak como padrão
        assert isinstance(provider, KeycloakProvider)


@pytest.mark.asyncio
class TestKeycloakProvider:
    """Testes para KeycloakProvider"""
    
    @pytest.mark.asyncio
    async def test_get_discovery_metadata(self, keycloak_provider):
        """Testar obtenção de metadados de descoberta"""
        mock_metadata = {
            "issuer": "https://keycloak.example.com/realms/sistema-laudos",
            "authorization_endpoint": "https://keycloak.example.com/auth",
            "token_endpoint": "https://keycloak.example.com/token",
            "jwks_uri": "https://keycloak.example.com/certs",
        }
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_metadata
            mock_get.return_value = mock_response
            
            metadata = await keycloak_provider.get_discovery_metadata()
            
            assert metadata["issuer"]
            assert "jwks_uri" in metadata
    
    def test_adapt_claims(self, keycloak_provider, sample_claims):
        """Testar adaptação de claims"""
        identity = keycloak_provider.adapt_claims(sample_claims)
        
        assert identity.email == "user@example.com"
        assert identity.roles == ["analista", "revisor"]


class TestIntegration:
    """Testes de integração"""
    
    def test_end_to_end_identity_creation(self, sample_claims):
        """Testar criação completa de identidade"""
        # Simular fluxo completo
        provider = KeycloakProvider(OIDCConfig(
            authority="https://keycloak.example.com/realms/sistema-laudos",
            client_id="sistema-laudos-web",
        ))
        
        identity = provider.adapt_claims(sample_claims)
        
        assert identity.email == "user@example.com"
        assert identity.has_role("analista")
        assert not identity.is_expired()
        assert identity.tenant_id == "tenant-123"
    
    def test_multiple_providers_same_claims(self, sample_claims):
        """Testar que diferentes providers adaptam claims corretamente"""
        keycloak_provider = KeycloakProvider(OIDCConfig(
            authority="https://keycloak.example.com/realms/sistema-laudos",
            client_id="sistema-laudos-web",
        ))
        
        identity = keycloak_provider.adapt_claims(sample_claims)
        
        # A estrutura deve ser consistente
        assert hasattr(identity, "sub")
        assert hasattr(identity, "email")
        assert hasattr(identity, "roles")
        assert hasattr(identity, "tenant_id")

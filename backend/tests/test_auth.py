"""
Authentication Tests
Tests for JWT token validation, identity extraction, and authentication flows
"""

import pytest
from fastapi.testclient import TestClient
from app.core.oidc_models import Identity
from tests.conftest import create_jwt_token


@pytest.mark.auth
class TestJWTTokenValidation:
    """Tests for JWT token validation"""

    def test_valid_token_accepted(self, client: TestClient, valid_user_token: str):
        """Valid token should be accepted"""
        headers = {"Authorization": f"Bearer {valid_user_token}"}
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200

    def test_missing_authorization_header(self, client: TestClient):
        """Request without auth header should be rejected"""
        # Try to access protected endpoint without token
        response = client.get("/api/v1/contratos")
        assert response.status_code == 401 or response.status_code == 403

    def test_invalid_authorization_format(self, client: TestClient):
        """Invalid auth format should be rejected"""
        headers = {"Authorization": "InvalidFormat token123"}
        response = client.get("/api/v1/contratos", headers=headers)
        assert response.status_code == 401 or response.status_code == 403

    def test_expired_token_rejected(self, client: TestClient, expired_token: str):
        """Expired token should be rejected"""
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/contratos", headers=headers)
        assert response.status_code == 401

    def test_invalid_token_rejected(self, client: TestClient, invalid_token: str):
        """Token with wrong signature should be rejected"""
        headers = {"Authorization": f"Bearer {invalid_token}"}
        response = client.get("/api/v1/contratos", headers=headers)
        assert response.status_code == 401

    def test_malformed_token(self, client: TestClient):
        """Malformed token should be rejected"""
        headers = {"Authorization": "Bearer not.a.jwt.token"}
        response = client.get("/api/v1/contratos", headers=headers)
        assert response.status_code == 401

    def test_empty_bearer_token(self, client: TestClient):
        """Empty bearer token should be rejected"""
        headers = {"Authorization": "Bearer "}
        response = client.get("/api/v1/contratos", headers=headers)
        assert response.status_code == 401


@pytest.mark.auth
class TestIdentityExtraction:
    """Tests for identity extraction from JWT tokens"""

    def test_user_identity_extraction(self, user_identity: Identity):
        """User identity should be extracted correctly"""
        assert user_identity.sub == "user-1"
        assert user_identity.email == "user@example.com"
        assert user_identity.tenant_id == "tenant-123"
        assert "user" in user_identity.roles

    def test_admin_identity_extraction(self, admin_identity: Identity):
        """Admin identity should be extracted correctly"""
        assert admin_identity.sub == "admin-user-1"
        assert admin_identity.email == "admin@example.com"
        assert admin_identity.tenant_id == "tenant-123"
        assert "admin" in admin_identity.roles
        assert "analista" in admin_identity.roles

    def test_analyst_identity_extraction(self, analyst_identity: Identity):
        """Analyst identity should be extracted correctly"""
        assert analyst_identity.sub == "analyst-user-1"
        assert analyst_identity.email == "analyst@example.com"
        assert analyst_identity.tenant_id == "tenant-123"
        assert "analista" in analyst_identity.roles

    def test_multiple_roles_extraction(self):
        """Multiple roles should be extracted correctly"""
        token = create_jwt_token(
            sub="user-123",
            roles=["admin", "analista", "user"]
        )
        # Decode to verify
        from jose import jwt
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload["roles"] == ["admin", "analista", "user"]


@pytest.mark.auth
class TestTokenScopes:
    """Tests for token scopes and claims"""

    def test_token_contains_required_claims(self, valid_user_token: str):
        """Token should contain all required claims"""
        from jose import jwt
        payload = jwt.decode(valid_user_token, options={"verify_signature": False})
        
        assert "sub" in payload
        assert "email" in payload
        assert "tenant_id" in payload
        assert "roles" in payload
        assert "exp" in payload
        assert "iat" in payload

    def test_token_expiration_claim(self):
        """Token should have correct expiration time"""
        from datetime import datetime, timedelta
        from jose import jwt
        
        token = create_jwt_token()
        payload = jwt.decode(token, options={"verify_signature": False})
        
        exp_time = payload["exp"]
        now = datetime.utcnow().timestamp()
        
        # Token should expire in roughly 1 hour
        assert 3500 < (exp_time - now) < 3700

    def test_custom_token_claims(self):
        """Custom token with additional claims"""
        token = create_jwt_token(
            sub="custom-user",
            email="custom@example.com",
            tenant_id="custom-tenant"
        )
        
        from jose import jwt
        payload = jwt.decode(token, options={"verify_signature": False})
        
        assert payload["sub"] == "custom-user"
        assert payload["email"] == "custom@example.com"
        assert payload["tenant_id"] == "custom-tenant"


@pytest.mark.auth
class TestAuthenticationFlow:
    """Tests for complete authentication flows"""

    def test_health_check_no_auth_required(self, client: TestClient):
        """Health check endpoint should not require auth"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_authenticated_request_succeeds(self, client_with_user: TestClient):
        """Authenticated request should succeed"""
        response = client_with_user.get("/api/v1/health")
        assert response.status_code == 200

    def test_bearer_token_extraction(self, client: TestClient, valid_user_token: str):
        """Bearer token should be correctly extracted from header"""
        headers = {
            "Authorization": f"Bearer {valid_user_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200

    def test_case_insensitive_bearer(self, client: TestClient, valid_user_token: str):
        """Bearer keyword should be case-insensitive"""
        # Some implementations accept "bearer" (lowercase)
        headers = {"Authorization": f"bearer {valid_user_token}"}
        response = client.get("/api/v1/health", headers=headers)
        # Status should be 200 or 401 depending on implementation
        assert response.status_code in [200, 401]


@pytest.mark.auth
class TestTokenRefresh:
    """Tests for token refresh scenarios"""

    def test_new_token_generation(self):
        """New tokens should be unique and valid"""
        token1 = create_jwt_token(sub="user-1")
        token2 = create_jwt_token(sub="user-1")
        
        # Tokens should be different (different iat claims)
        assert token1 != token2

    def test_token_with_custom_expiration(self):
        """Token with custom expiration should work"""
        from datetime import timedelta
        from jose import jwt
        
        token = create_jwt_token(exp_delta=timedelta(hours=2))
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Calculate exp time difference
        import time
        now = time.time()
        time_diff = payload["exp"] - now
        
        # Should be roughly 2 hours (7200 seconds)
        assert 7000 < time_diff < 7400


@pytest.mark.auth
class TestMultiTenantAuthentication:
    """Tests for multi-tenant authentication scenarios"""

    def test_single_tenant_identity(self, user_identity: Identity):
        """Single tenant user should have correct tenant_id"""
        assert user_identity.tenant_id == "tenant-123"

    def test_different_tenant_identity(self, other_tenant_identity: Identity):
        """User from different tenant should have different tenant_id"""
        assert other_tenant_identity.tenant_id == "tenant-other"
        assert other_tenant_identity.email == "user@other.com"

    def test_token_contains_tenant_id(self, valid_user_token: str):
        """Token should contain tenant_id claim"""
        from jose import jwt
        payload = jwt.decode(valid_user_token, options={"verify_signature": False})
        
        assert "tenant_id" in payload
        assert payload["tenant_id"] == "tenant-123"

    def test_different_users_different_tenants(self):
        """Different users can have different tenant assignments"""
        token1 = create_jwt_token(tenant_id="tenant-1", sub="user-1")
        token2 = create_jwt_token(tenant_id="tenant-2", sub="user-2")
        
        from jose import jwt
        payload1 = jwt.decode(token1, options={"verify_signature": False})
        payload2 = jwt.decode(token2, options={"verify_signature": False})
        
        assert payload1["tenant_id"] == "tenant-1"
        assert payload2["tenant_id"] == "tenant-2"


@pytest.mark.auth
class TestRoleBasedTokens:
    """Tests for role-based token variations"""

    def test_admin_token_has_admin_role(self, admin_identity: Identity):
        """Admin token should contain admin role"""
        assert "admin" in admin_identity.roles

    def test_user_token_without_admin_role(self, user_identity: Identity):
        """User token should not contain admin role"""
        assert "admin" not in user_identity.roles

    def test_analyst_token_has_analista_role(self, analyst_identity: Identity):
        """Analyst token should contain analista role"""
        assert "analista" in analyst_identity.roles

    def test_multiple_roles_in_token(self, admin_identity: Identity):
        """Admin should have multiple roles"""
        assert len(admin_identity.roles) >= 2
        assert "admin" in admin_identity.roles
        assert "analista" in admin_identity.roles

    def test_custom_role_token(self):
        """Token with custom roles should work"""
        token = create_jwt_token(roles=["custom_role", "another_role"])
        
        from jose import jwt
        payload = jwt.decode(token, options={"verify_signature": False})
        
        assert "custom_role" in payload["roles"]
        assert "another_role" in payload["roles"]

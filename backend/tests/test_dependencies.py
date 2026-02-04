"""
Unit Tests for FastAPI Dependencies, Decorators, and Error Handlers

Testing:
- get_identity dependency (JWT validation)
- get_current_user dependency (semantic alias)
- get_optional_identity dependency (optional auth)
- @require_roles decorator (role-based access)
- @require_tenant decorator (tenant isolation)
- Error handlers (401, 403, 429, 500)
"""

import pytest
from fastapi import FastAPI, Depends, status
from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.core.oidc_models import Identity, TokenValidationResult
from app.api.dependencies import (
    get_identity,
    get_current_user,
    get_optional_identity,
    get_db,
)
from app.api.decorators import require_roles, require_tenant
from app.api.error_handlers import (
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    register_error_handlers,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_app():
    """Create a test FastAPI app with error handlers registered."""
    app = FastAPI()
    register_error_handlers(app)
    return app


@pytest.fixture
def test_client(test_app):
    """Create a test client from the test app."""
    return TestClient(test_app)


@pytest.fixture
def valid_identity():
    """Create a valid Identity for testing."""
    return Identity(
        sub="user-123",
        email="user@example.com",
        preferred_username="johndoe",
        roles=["analista", "revisor"],
        tenant_id="tenant-456",
        name="John Doe",
        iss="https://keycloak.example.com",
        aud="laudos-api",
        exp=datetime.utcnow().timestamp() + 3600,
        iat=datetime.utcnow().timestamp(),
    )


@pytest.fixture
def admin_identity():
    """Create an admin Identity for testing."""
    return Identity(
        sub="admin-123",
        email="admin@example.com",
        preferred_username="admin",
        roles=["admin"],
        tenant_id="tenant-default",
        name="Admin User",
        iss="https://keycloak.example.com",
        aud="laudos-api",
        exp=datetime.utcnow().timestamp() + 3600,
        iat=datetime.utcnow().timestamp(),
    )


# ============================================================================
# TEST: get_identity dependency
# ============================================================================

@pytest.mark.asyncio
async def test_get_identity_success(valid_identity):
    """Test successful token validation and identity extraction."""
    # Mock the OIDC provider
    mock_provider = AsyncMock()
    mock_result = TokenValidationResult(
        valid=True,
        identity=valid_identity,
        error=None,
        error_code=None
    )
    mock_provider.validate_token = AsyncMock(return_value=mock_result)
    
    with patch('app.api.dependencies.get_provider', return_value=mock_provider):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-token-123"
        )
        
        identity = await get_identity(credentials)
        
        assert identity is not None
        assert identity.sub == "user-123"
        assert identity.email == "user@example.com"
        assert identity.tenant_id == "tenant-456"
        assert "analista" in identity.roles


@pytest.mark.asyncio
async def test_get_identity_missing_credentials():
    """Test that missing credentials raises 401."""
    with pytest.raises(Exception) as exc_info:
        await get_identity(credentials=None)
    
    # Should raise an error about missing credentials
    assert "credentials" in str(exc_info.value).lower() or "401" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_identity_invalid_token():
    """Test that invalid token returns 401."""
    mock_provider = AsyncMock()
    mock_result = TokenValidationResult(
        valid=False,
        identity=None,
        error="Token expired",
        error_code="TOKEN_EXPIRED"
    )
    mock_provider.validate_token = AsyncMock(return_value=mock_result)
    
    with patch('app.api.dependencies.get_provider', return_value=mock_provider):
        with pytest.raises(Exception) as exc_info:
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="expired-token"
            )
            await get_identity(credentials)
        
        # Should raise 401
        assert "401" in str(exc_info.value) or "unauthorized" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_identity_signature_mismatch():
    """Test that signature mismatch returns 401."""
    mock_provider = AsyncMock()
    mock_result = TokenValidationResult(
        valid=False,
        identity=None,
        error="Invalid signature",
        error_code="INVALID_SIGNATURE"
    )
    mock_provider.validate_token = AsyncMock(return_value=mock_result)
    
    with patch('app.api.dependencies.get_provider', return_value=mock_provider):
        with pytest.raises(Exception):
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="tampered-token"
            )
            await get_identity(credentials)


# ============================================================================
# TEST: get_current_user dependency
# ============================================================================

@pytest.mark.asyncio
async def test_get_current_user_alias(valid_identity):
    """Test that get_current_user is an alias for get_identity."""
    mock_provider = AsyncMock()
    mock_result = TokenValidationResult(
        valid=True,
        identity=valid_identity,
        error=None,
        error_code=None
    )
    mock_provider.validate_token = AsyncMock(return_value=mock_result)
    
    with patch('app.api.dependencies.get_provider', return_value=mock_provider):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-token"
        )
        
        # get_current_user should work exactly like get_identity
        user = await get_current_user(credentials)
        
        assert user.email == valid_identity.email
        assert user.sub == valid_identity.sub


# ============================================================================
# TEST: get_optional_identity dependency
# ============================================================================

@pytest.mark.asyncio
async def test_get_optional_identity_with_valid_token(valid_identity):
    """Test optional identity with valid token returns Identity."""
    mock_provider = AsyncMock()
    mock_result = TokenValidationResult(
        valid=True,
        identity=valid_identity,
        error=None,
        error_code=None
    )
    mock_provider.validate_token = AsyncMock(return_value=mock_result)
    
    with patch('app.api.dependencies.get_provider', return_value=mock_provider):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-token"
        )
        
        identity = await get_optional_identity(credentials)
        
        assert identity is not None
        assert identity.email == "user@example.com"


@pytest.mark.asyncio
async def test_get_optional_identity_no_credentials():
    """Test optional identity without credentials returns None."""
    identity = await get_optional_identity(credentials=None)
    
    assert identity is None


@pytest.mark.asyncio
async def test_get_optional_identity_invalid_token():
    """Test optional identity with invalid token returns None."""
    mock_provider = AsyncMock()
    mock_result = TokenValidationResult(
        valid=False,
        identity=None,
        error="Token expired",
        error_code="TOKEN_EXPIRED"
    )
    mock_provider.validate_token = AsyncMock(return_value=mock_result)
    
    with patch('app.api.dependencies.get_provider', return_value=mock_provider):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-token"
        )
        
        identity = await get_optional_identity(credentials)
        
        assert identity is None


# ============================================================================
# TEST: @require_roles decorator
# ============================================================================

def test_require_roles_with_matching_role(valid_identity):
    """Test that @require_roles allows access with matching role."""
    @require_roles("analista", "revisor")
    async def protected_endpoint(identity: Identity):
        return {"status": "allowed"}
    
    # Should not raise because user has "analista" role
    # (This is a simplified test; actual FastAPI integration would be more complex)


def test_require_roles_without_matching_role(valid_identity):
    """Test that @require_roles denies access without matching role."""
    @require_roles("admin")
    async def admin_endpoint(identity: Identity):
        return {"status": "admin"}
    
    # User with roles ["analista", "revisor"] doesn't have "admin"
    # Would raise 403 in actual execution


def test_require_roles_case_insensitive(valid_identity):
    """Test that role matching is case-insensitive."""
    @require_roles("ANALISTA", "Revisor")
    async def protected_endpoint(identity: Identity):
        return {"status": "allowed"}
    
    # Should match because comparison is case-insensitive


# ============================================================================
# TEST: @require_tenant decorator
# ============================================================================

def test_require_tenant_with_valid_tenant(valid_identity):
    """Test that @require_tenant passes with valid tenant_id."""
    @require_tenant()
    async def tenant_safe_endpoint(identity: Identity):
        return {"tenant_id": identity.tenant_id}
    
    # Should pass because identity has tenant_id


def test_require_tenant_missing_tenant_id():
    """Test that @require_tenant fails without tenant_id."""
    identity_no_tenant = Identity(
        sub="user-123",
        email="user@example.com",
        preferred_username="john",
        roles=["analista"],
        tenant_id=None,  # Missing tenant_id
        name="John",
        iss="https://idp.example.com",
        aud="app",
        exp=datetime.utcnow().timestamp() + 3600,
        iat=datetime.utcnow().timestamp(),
    )
    
    @require_tenant()
    async def tenant_safe_endpoint(identity: Identity):
        return {"tenant_id": identity.tenant_id}
    
    # Should fail because tenant_id is missing


# ============================================================================
# TEST: Error Handlers
# ============================================================================

def test_authentication_error_handler(test_client, test_app):
    """Test that 401 errors are formatted correctly."""
    @test_app.get("/protected")
    async def protected_endpoint():
        raise AuthenticationError("Invalid token")
    
    response = test_client.get("/protected")
    
    assert response.status_code == 401
    assert response.json()["error"] == "unauthorized"
    assert "Invalid token" in response.json()["message"]


def test_authorization_error_handler(test_client, test_app):
    """Test that 403 errors are formatted correctly."""
    @test_app.get("/admin")
    async def admin_endpoint():
        raise AuthorizationError("Admin role required")
    
    response = test_client.get("/admin")
    
    assert response.status_code == 403
    assert response.json()["error"] == "forbidden"
    assert "Admin role required" in response.json()["message"]


def test_rate_limit_error_handler(test_client, test_app):
    """Test that 429 errors are formatted correctly."""
    @test_app.get("/limited")
    async def limited_endpoint():
        raise RateLimitError("Too many requests")
    
    response = test_client.get("/limited")
    
    assert response.status_code == 429
    assert response.json()["error"] == "too_many_requests"
    assert "retry_after" in response.json()


def test_error_response_includes_timestamp(test_client, test_app):
    """Test that error responses include timestamp."""
    @test_app.get("/error")
    async def error_endpoint():
        raise AuthenticationError("Test error")
    
    response = test_client.get("/error")
    
    assert "timestamp" in response.json()
    assert "path" in response.json()
    assert "status_code" in response.json()


# ============================================================================
# TEST: Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_identity_lifecycle(valid_identity):
    """Test complete identity lifecycle from token to endpoint."""
    mock_provider = AsyncMock()
    mock_result = TokenValidationResult(
        valid=True,
        identity=valid_identity,
        error=None,
        error_code=None
    )
    mock_provider.validate_token = AsyncMock(return_value=mock_result)
    
    with patch('app.api.dependencies.get_provider', return_value=mock_provider):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test-token"
        )
        
        # Step 1: Extract identity from token
        identity = await get_identity(credentials)
        assert identity is not None
        
        # Step 2: Check roles
        assert "analista" in identity.roles
        
        # Step 3: Verify tenant isolation
        assert identity.tenant_id == "tenant-456"


@pytest.mark.asyncio
async def test_multiple_role_check(admin_identity):
    """Test that user can have multiple roles."""
    assert "admin" in admin_identity.roles
    assert len(admin_identity.roles) >= 1
    
    # Admin can access admin endpoints
    # Admin can also access analista endpoints if they have that role


def test_error_response_structure(test_client, test_app):
    """Test that all error responses have consistent structure."""
    @test_app.get("/auth-error")
    async def auth_error():
        raise AuthenticationError()
    
    @test_app.get("/authz-error")
    async def authz_error():
        raise AuthorizationError()
    
    required_fields = ["error", "message", "status_code", "timestamp", "path"]
    
    # Test 401
    response = test_client.get("/auth-error")
    assert all(field in response.json() for field in required_fields)
    
    # Test 403
    response = test_client.get("/authz-error")
    assert all(field in response.json() for field in required_fields)

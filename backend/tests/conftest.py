"""
Pytest Configuration and Global Fixtures
Provides fixtures for:
- FastAPI test client
- JWT tokens (valid, invalid, expired)
- User identities (admin, analista, user)
- Database session
- Mock data
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Generator, Dict, Any
from unittest.mock import MagicMock, patch
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import Base
from app.api.dependencies import get_db, get_identity
from app.core.oidc_models import Identity


# ============================================================================
# Database Configuration for Tests
# ============================================================================

# Use in-memory SQLite for faster tests
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator:
    """Override get_db dependency with test database"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# ============================================================================
# JWT Token Fixtures
# ============================================================================

TEST_SECRET_KEY = "test-secret-key-for-jwt-signing-very-long"
ALGORITHM = "HS256"


def create_jwt_token(
    sub: str = "user-123",
    email: str = "user@example.com",
    tenant_id: str = "tenant-123",
    roles: list = None,
    exp_delta: timedelta = None,
    secret_key: str = TEST_SECRET_KEY,
) -> str:
    """Create a JWT token for testing"""
    if roles is None:
        roles = ["user"]
    
    if exp_delta is None:
        exp_delta = timedelta(hours=1)
    
    payload = {
        "sub": sub,
        "email": email,
        "tenant_id": tenant_id,
        "roles": roles,
        "exp": datetime.utcnow() + exp_delta,
        "iat": datetime.utcnow(),
    }
    
    return jwt.encode(payload, secret_key, algorithm=ALGORITHM)


@pytest.fixture
def valid_admin_token() -> str:
    """JWT token for admin user"""
    return create_jwt_token(
        sub="admin-user-1",
        email="admin@example.com",
        tenant_id="tenant-123",
        roles=["admin", "analista"],
    )


@pytest.fixture
def valid_analyst_token() -> str:
    """JWT token for analyst user"""
    return create_jwt_token(
        sub="analyst-user-1",
        email="analyst@example.com",
        tenant_id="tenant-123",
        roles=["analista"],
    )


@pytest.fixture
def valid_user_token() -> str:
    """JWT token for regular user"""
    return create_jwt_token(
        sub="user-1",
        email="user@example.com",
        tenant_id="tenant-123",
        roles=["user"],
    )


@pytest.fixture
def valid_token_other_tenant() -> str:
    """JWT token for user from different tenant"""
    return create_jwt_token(
        sub="user-other",
        email="user@other.com",
        tenant_id="tenant-other",
        roles=["user"],
    )


@pytest.fixture
def expired_token() -> str:
    """Expired JWT token"""
    return create_jwt_token(
        exp_delta=timedelta(hours=-1)  # Expired 1 hour ago
    )


@pytest.fixture
def invalid_token() -> str:
    """Invalid JWT token (wrong signature)"""
    return jwt.encode(
        {"sub": "user", "exp": datetime.utcnow() + timedelta(hours=1)},
        "wrong-secret-key",
        algorithm=ALGORITHM,
    )


# ============================================================================
# Identity Fixtures
# ============================================================================

@pytest.fixture
def admin_identity() -> Identity:
    """Identity object for admin user"""
    return Identity(
        sub="admin-user-1",
        email="admin@example.com",
        tenant_id="tenant-123",
        roles=["admin", "analista"],
    )


@pytest.fixture
def analyst_identity() -> Identity:
    """Identity object for analyst user"""
    return Identity(
        sub="analyst-user-1",
        email="analyst@example.com",
        tenant_id="tenant-123",
        roles=["analista"],
    )


@pytest.fixture
def user_identity() -> Identity:
    """Identity object for regular user"""
    return Identity(
        sub="user-1",
        email="user@example.com",
        tenant_id="tenant-123",
        roles=["user"],
    )


@pytest.fixture
def other_tenant_identity() -> Identity:
    """Identity object for user from different tenant"""
    return Identity(
        sub="user-other",
        email="user@other.com",
        tenant_id="tenant-other",
        roles=["user"],
    )


# ============================================================================
# FastAPI TestClient Fixtures
# ============================================================================

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session) -> TestClient:
    """Create a TestClient with overridden database dependency"""
    app.dependency_overrides[get_db] = lambda: db_session
    
    client = TestClient(app)
    
    yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_admin(client: TestClient, valid_admin_token: str) -> TestClient:
    """TestClient with admin authorization headers"""
    client.headers = {
        "Authorization": f"Bearer {valid_admin_token}",
        "Content-Type": "application/json",
    }
    return client


@pytest.fixture
def client_with_analyst(client: TestClient, valid_analyst_token: str) -> TestClient:
    """TestClient with analyst authorization headers"""
    client.headers = {
        "Authorization": f"Bearer {valid_analyst_token}",
        "Content-Type": "application/json",
    }
    return client


@pytest.fixture
def client_with_user(client: TestClient, valid_user_token: str) -> TestClient:
    """TestClient with regular user authorization headers"""
    client.headers = {
        "Authorization": f"Bearer {valid_user_token}",
        "Content-Type": "application/json",
    }
    return client


@pytest.fixture
def client_with_other_tenant(client: TestClient, valid_token_other_tenant: str) -> TestClient:
    """TestClient with authorization from different tenant"""
    client.headers = {
        "Authorization": f"Bearer {valid_token_other_tenant}",
        "Content-Type": "application/json",
    }
    return client


# ============================================================================
# Mock Identity Fixtures (for dependency injection)
# ============================================================================

@pytest.fixture
def mock_get_identity_admin(admin_identity: Identity):
    """Mock get_identity dependency to return admin identity"""
    def _mock():
        return admin_identity
    return _mock


@pytest.fixture
def mock_get_identity_analyst(analyst_identity: Identity):
    """Mock get_identity dependency to return analyst identity"""
    def _mock():
        return analyst_identity
    return _mock


@pytest.fixture
def mock_get_identity_user(user_identity: Identity):
    """Mock get_identity dependency to return user identity"""
    def _mock():
        return user_identity
    return _mock


# ============================================================================
# Event Loop for Async Tests
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def mock_contrato_data() -> Dict[str, Any]:
    """Mock contract data for testing"""
    return {
        "numero_contrato": "CONT-2024-001",
        "cliente": "Acme Corporation",
        "valor": 50000.00,
        "data_inicio": "2024-01-01",
        "data_fim": "2024-12-31",
        "status": "ativo",
    }


@pytest.fixture
def mock_parecer_data() -> Dict[str, Any]:
    """Mock opinion/verdict data for testing"""
    return {
        "contrato_id": 1,
        "analista_id": "analyst-1",
        "parecer": "Documento em conformidade com as normas exigidas",
        "status": "aprovado",
        "data_parecer": "2024-02-03",
    }


@pytest.fixture
def mock_bureau_data() -> Dict[str, Any]:
    """Mock bureau data for testing"""
    return {
        "contrato_id": 1,
        "score_credito": 750,
        "restricoes": [],
        "status": "aprovado",
    }


@pytest.fixture
def mock_geolocalizacao_data() -> Dict[str, Any]:
    """Mock geolocation analysis data for testing"""
    return {
        "contrato_id": 1,
        "endereco": "Rua Principal 123, São Paulo, SP",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "distancia_matriz": 15.5,
        "status": "verificado",
    }


# ============================================================================
# Pytest Markers and Hooks
# ============================================================================

def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "auth: mark test as authentication test"
    )
    config.addinivalue_line(
        "markers", "authz: mark test as authorization test"
    )
    config.addinivalue_line(
        "markers", "tenant: mark test as tenant isolation test"
    )
    config.addinivalue_line(
        "markers", "rate_limit: mark test as rate limiting test"
    )
    config.addinivalue_line(
        "markers", "audit: mark test as audit logging test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def auth_headers(valid_user_token: str) -> Dict[str, str]:
    """Standard authorization headers with user token"""
    return {
        "Authorization": f"Bearer {valid_user_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture
def admin_headers(valid_admin_token: str) -> Dict[str, str]:
    """Standard authorization headers with admin token"""
    return {
        "Authorization": f"Bearer {valid_admin_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture
def no_auth_headers() -> Dict[str, str]:
    """Headers without authorization (for testing 401)"""
    return {
        "Content-Type": "application/json",
    }

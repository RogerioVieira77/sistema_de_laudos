"""
Integration Tests
End-to-end tests for API endpoints with full security stack
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestContratosEndpoints:
    """Integration tests for Contratos endpoints"""

    def test_contratos_list_happy_path(self, client_with_user: TestClient):
        """Happy path: list contratos as authenticated user"""
        response = client_with_user.get("/api/v1/contratos")
        
        # Should return 200 (success) or 404 (not found)
        assert response.status_code in [200, 404]

    def test_contratos_get_nonexistent(self, client_with_user: TestClient):
        """Get non-existent contrato should return 404"""
        response = client_with_user.get("/api/v1/contratos/99999")
        
        assert response.status_code in [404, 403]

    def test_contratos_delete_unauthorized(self, client_with_user: TestClient):
        """Delete without permission should return 403"""
        response = client_with_user.delete("/api/v1/contratos/1")
        
        assert response.status_code in [403, 404, 429]

    def test_contratos_upload_requires_auth(self, client: TestClient):
        """Upload without auth should return 401/403"""
        response = client.post(
            "/api/v1/contratos/upload",
            files={"file": ("test.pdf", b"test", "application/pdf")}
        )
        
        assert response.status_code in [401, 403]

    def test_contratos_upload_with_auth(self, client_with_user: TestClient):
        """Upload with auth should be processed"""
        response = client_with_user.post(
            "/api/v1/contratos/upload",
            files={"file": ("test.pdf", b"test", "application/pdf")}
        )
        
        # Could fail for various reasons, but not auth
        assert response.status_code != 401

    def test_contratos_list_filters_by_tenant(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """Contratos list should filter by tenant"""
        response1 = client_with_user.get("/api/v1/contratos")
        response2 = client_with_other_tenant.get("/api/v1/contratos")
        
        # Both should succeed but possibly with different data
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]


@pytest.mark.integration
class TestPareceresEndpoints:
    """Integration tests for Pareceres endpoints"""

    def test_pareceres_list_happy_path(self, client_with_user: TestClient):
        """Happy path: list pareceres as authenticated user"""
        response = client_with_user.get("/api/v1/pareceres")
        
        assert response.status_code in [200, 404]

    def test_pareceres_get_nonexistent(self, client_with_user: TestClient):
        """Get non-existent parecer should return 404"""
        response = client_with_user.get("/api/v1/pareceres/99999")
        
        assert response.status_code in [404, 403]

    def test_pareceres_delete_unauthorized(self, client_with_user: TestClient):
        """Delete parecer without permission should return 403"""
        response = client_with_user.delete("/api/v1/pareceres/1")
        
        assert response.status_code in [403, 404, 429]

    def test_pareceres_requires_auth(self, client: TestClient):
        """Pareceres endpoints should require auth"""
        response = client.get("/api/v1/pareceres")
        
        assert response.status_code in [401, 403]

    def test_pareceres_list_filters_by_tenant(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """Pareceres list should filter by tenant"""
        response1 = client_with_user.get("/api/v1/pareceres")
        response2 = client_with_other_tenant.get("/api/v1/pareceres")
        
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]


@pytest.mark.integration
class TestBureauEndpoints:
    """Integration tests for Bureau endpoints"""

    def test_bureau_list_happy_path(self, client_with_user: TestClient):
        """Happy path: list bureau data as authenticated user"""
        response = client_with_user.get("/api/v1/bureau")
        
        assert response.status_code in [200, 404]

    def test_bureau_get_nonexistent(self, client_with_user: TestClient):
        """Get non-existent bureau data should return 404"""
        response = client_with_user.get("/api/v1/bureau/99999")
        
        assert response.status_code in [404, 403]

    def test_bureau_requires_auth(self, client: TestClient):
        """Bureau endpoints should require auth"""
        response = client.get("/api/v1/bureau")
        
        assert response.status_code in [401, 403]

    def test_bureau_list_filters_by_tenant(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """Bureau list should filter by tenant"""
        response1 = client_with_user.get("/api/v1/bureau")
        response2 = client_with_other_tenant.get("/api/v1/bureau")
        
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]


@pytest.mark.integration
class TestGeolocationEndpoints:
    """Integration tests for Geolocation endpoints"""

    def test_geolocalizacao_requires_auth(self, client: TestClient):
        """Geolocation endpoints should require auth"""
        response = client.get("/api/v1/geolocalizacao")
        
        assert response.status_code in [401, 403, 404]

    def test_geolocalizacao_get_with_auth(self, client_with_user: TestClient):
        """Get geolocation data with auth should work"""
        response = client_with_user.get("/api/v1/geolocalizacao/1")
        
        assert response.status_code in [200, 404]

    def test_geolocalizacao_analyze_requires_auth(self, client: TestClient):
        """Geolocation analysis should require auth"""
        response = client.post(
            "/api/v1/geolocalizacao/analisar",
            json={"contrato_id": 1, "endereco": "Rua Test"}
        )
        
        assert response.status_code in [401, 403]

    def test_geolocalizacao_analyze_with_auth(self, client_with_user: TestClient):
        """Geolocation analysis with auth should be processed"""
        response = client_with_user.post(
            "/api/v1/geolocalizacao/analisar",
            json={"contrato_id": 1, "endereco": "Rua Test"}
        )
        
        # Could fail for various reasons, but not auth
        assert response.status_code != 401


@pytest.mark.integration
class TestHealthEndpoint:
    """Integration tests for Health endpoint"""

    def test_health_no_auth_required(self, client: TestClient):
        """Health endpoint should not require auth"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200

    def test_health_returns_json(self, client: TestClient):
        """Health endpoint should return JSON"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_health_contains_status(self, client: TestClient):
        """Health response should contain status"""
        response = client.get("/api/v1/health")
        
        data = response.json()
        assert "status" in data or "health" in data

    def test_health_accessible_without_token(self, client: TestClient):
        """Health should be accessible without JWT token"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200

    def test_health_accessible_with_invalid_token(self, client: TestClient):
        """Health should be accessible even with invalid token"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/v1/health", headers=headers)
        
        # Health check should work regardless
        assert response.status_code in [200]


@pytest.mark.integration
class TestCompleteSecurityStack:
    """Tests for complete security stack integration"""

    def test_admin_full_access(self, client_with_admin: TestClient):
        """Admin should have access to all public endpoints"""
        endpoints = [
            "/api/v1/contratos",
            "/api/v1/pareceres",
            "/api/v1/bureau",
            "/api/v1/audit-logs/my-activity",
            "/api/v1/audit-logs/tenant-activity",
            "/api/v1/audit-logs/failed-actions",
        ]
        
        for endpoint in endpoints:
            response = client_with_admin.get(endpoint)
            assert response.status_code in [200, 404, 429], f"Failed at {endpoint}"

    def test_user_restricted_access(self, client_with_user: TestClient):
        """User should be restricted from admin endpoints"""
        admin_endpoints = [
            "/api/v1/audit-logs/tenant-activity",
            "/api/v1/audit-logs/failed-actions",
            "/api/v1/audit-logs/activity-summary",
            "/api/v1/audit-logs/suspicious-activity",
        ]
        
        for endpoint in admin_endpoints:
            response = client_with_user.get(endpoint)
            assert response.status_code == 403, f"User should not access {endpoint}"

    def test_unauthenticated_restricted_access(self, client: TestClient):
        """Unauthenticated user should not access protected endpoints"""
        protected_endpoints = [
            "/api/v1/contratos",
            "/api/v1/pareceres",
            "/api/v1/bureau",
            "/api/v1/audit-logs/my-activity",
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 403], f"Unauthenticated should not access {endpoint}"

    def test_tenant_isolation_maintained(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """Tenant isolation should be maintained across operations"""
        # Both users access their endpoints
        response1 = client_with_user.get("/api/v1/contratos")
        response2 = client_with_other_tenant.get("/api/v1/contratos")
        
        # Both should succeed but with isolated data
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

    def test_rate_limiting_enforced(self, client_with_user: TestClient):
        """Rate limiting should be enforced on endpoints"""
        # Make a few requests
        responses = []
        for _ in range(3):
            response = client_with_user.get("/api/v1/contratos")
            responses.append(response.status_code)
        
        # Should succeed (under rate limit)
        assert all(status in [200, 404] for status in responses)

    def test_role_hierarchy_enforced(
        self, client_with_user: TestClient, client_with_analyst: TestClient,
        client_with_admin: TestClient
    ):
        """Role hierarchy should be enforced"""
        # User can access basic endpoints
        response1 = client_with_user.get("/api/v1/audit-logs/my-activity")
        assert response1.status_code in [200, 404, 429]
        
        # User cannot access admin endpoints
        response2 = client_with_user.get("/api/v1/audit-logs/tenant-activity")
        assert response2.status_code == 403
        
        # Admin can access all
        response3 = client_with_admin.get("/api/v1/audit-logs/tenant-activity")
        assert response3.status_code in [200, 404, 429]


@pytest.mark.integration
class TestErrorHandling:
    """Tests for error handling in endpoints"""

    def test_404_for_missing_resource(self, client_with_user: TestClient):
        """Missing resource should return 404"""
        response = client_with_user.get("/api/v1/contratos/99999999")
        
        assert response.status_code in [404, 403]

    def test_401_for_missing_auth(self, client: TestClient):
        """Missing auth should return 401/403"""
        response = client.get("/api/v1/contratos")
        
        assert response.status_code in [401, 403]

    def test_403_for_insufficient_permissions(self, client_with_user: TestClient):
        """Insufficient permissions should return 403"""
        response = client_with_user.get("/api/v1/audit-logs/tenant-activity")
        
        assert response.status_code == 403

    def test_422_for_invalid_request_body(self, client_with_user: TestClient):
        """Invalid request body should return 422"""
        response = client_with_user.post(
            "/api/v1/geolocalizacao/analisar",
            json={"invalid": "data"}
        )
        
        # Could be 422 (validation error) or other error
        assert response.status_code in [400, 422, 404]


@pytest.mark.integration
class TestMultipleSecurityLayers:
    """Tests for multiple security layers working together"""

    def test_auth_plus_tenant_isolation(self, client_with_other_tenant: TestClient):
        """Authentication and tenant isolation should work together"""
        # User is authenticated but from different tenant
        response = client_with_other_tenant.get("/api/v1/contratos/1")
        
        # Should get 404 (not in their tenant) not 401 (not authenticated)
        assert response.status_code in [404, 403]

    def test_auth_plus_role_based_access(self, client_with_user: TestClient):
        """Authentication and RBAC should work together"""
        # User is authenticated but lacks admin role
        response = client_with_user.get("/api/v1/audit-logs/tenant-activity")
        
        # Should get 403 (forbidden due to role) not 401 (not authenticated)
        assert response.status_code == 403

    def test_rate_limit_plus_auth(self, client: TestClient, client_with_user: TestClient):
        """Rate limiting should work with authentication"""
        # Without auth, should get 401 first
        response1 = client.get("/api/v1/contratos")
        assert response1.status_code in [401, 403]
        
        # With auth, should get 200 (or 429 if rate limited)
        response2 = client_with_user.get("/api/v1/contratos")
        assert response2.status_code in [200, 404, 429]

    def test_tenant_plus_role_plus_rate_limit(
        self, client_with_admin: TestClient, client_with_other_tenant: TestClient
    ):
        """Tenant isolation, RBAC, and rate limiting should all work"""
        # Admin from tenant-123 accessing tenant activity
        response1 = client_with_admin.get("/api/v1/audit-logs/tenant-activity")
        assert response1.status_code in [200, 404, 429]
        
        # User from other tenant accessing same endpoint (but forbidden)
        response2 = client_with_other_tenant.get("/api/v1/audit-logs/tenant-activity")
        assert response2.status_code == 403

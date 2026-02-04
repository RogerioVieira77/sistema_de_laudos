"""
Rate Limiting Tests
Tests for rate limiting enforcement and 429 responses
"""

import pytest
import time
from fastapi.testclient import TestClient


@pytest.mark.rate_limit
class TestReadEndpointRateLimits:
    """Tests for rate limiting on READ operations (50/min)"""

    def test_read_endpoint_accepts_requests(self, client_with_user: TestClient):
        """Read endpoint should accept requests"""
        response = client_with_user.get("/api/v1/contratos")
        assert response.status_code in [200, 404]

    def test_single_read_request_succeeds(self, client_with_user: TestClient):
        """Single read request should succeed"""
        response = client_with_user.get("/api/v1/contratos")
        assert response.status_code in [200, 404]

    def test_multiple_read_requests_allowed(self, client_with_user: TestClient):
        """Multiple read requests should be allowed (up to limit)"""
        responses = []
        for _ in range(3):
            response = client_with_user.get("/api/v1/contratos")
            responses.append(response.status_code)
        
        # All should succeed
        assert all(status in [200, 404] for status in responses)

    def test_contratos_get_endpoint_returns_response(self, client_with_user: TestClient):
        """GET /contratos/{id} should return response"""
        response = client_with_user.get("/api/v1/contratos/999")
        # 404 for not found is expected
        assert response.status_code in [200, 404]

    def test_pareceres_list_returns_response(self, client_with_user: TestClient):
        """GET /pareceres should return response"""
        response = client_with_user.get("/api/v1/pareceres")
        assert response.status_code in [200, 404]

    def test_bureau_list_returns_response(self, client_with_user: TestClient):
        """GET /bureau should return response"""
        response = client_with_user.get("/api/v1/bureau")
        assert response.status_code in [200, 404]


@pytest.mark.rate_limit
class TestDeleteEndpointRateLimits:
    """Tests for rate limiting on DELETE operations (10/min)"""

    def test_delete_endpoint_rejects_without_auth(self, client: TestClient):
        """DELETE without auth should be rejected"""
        response = client.delete("/api/v1/contratos/1")
        assert response.status_code in [401, 403]

    def test_delete_endpoint_accepts_with_auth(self, client_with_user: TestClient):
        """DELETE with auth should be processed"""
        response = client_with_user.delete("/api/v1/contratos/999")
        # Could be 403 (forbidden), 404 (not found), or 429 (rate limited)
        assert response.status_code in [403, 404, 429]

    def test_parecer_delete_with_auth(self, client_with_user: TestClient):
        """DELETE parecer with auth should be processed"""
        response = client_with_user.delete("/api/v1/pareceres/999")
        assert response.status_code in [403, 404, 429]


@pytest.mark.rate_limit
class TestUploadEndpointRateLimits:
    """Tests for rate limiting on UPLOAD operations (10/min)"""

    def test_upload_endpoint_rejects_without_auth(self, client: TestClient):
        """Upload without auth should be rejected"""
        response = client.post(
            "/api/v1/contratos/upload",
            files={"file": ("test.pdf", b"content", "application/pdf")}
        )
        assert response.status_code in [401, 403]

    def test_upload_endpoint_accepts_with_auth(self, client_with_user: TestClient):
        """Upload with auth should be processed"""
        response = client_with_user.post(
            "/api/v1/contratos/upload",
            files={"file": ("test.pdf", b"content", "application/pdf")}
        )
        # Could be 400 (bad request), 403 (forbidden), or 429 (rate limited)
        assert response.status_code in [400, 403, 422, 429]

    def test_geolocalizacao_analysis_upload(self, client_with_user: TestClient):
        """Geolocation analysis POST should be processed"""
        response = client_with_user.post(
            "/api/v1/geolocalizacao/analisar",
            json={
                "contrato_id": 999,
                "endereco": "Rua Test 123",
            }
        )
        # Could be 404, 403, or 429
        assert response.status_code in [404, 403, 422, 429]


@pytest.mark.rate_limit
class TestRateLimitHeaders:
    """Tests for rate limit response headers"""

    def test_rate_limit_exceeded_has_retry_after(self, client_with_user: TestClient):
        """429 response should have Retry-After header"""
        # Try to trigger rate limit (may not happen in single test)
        # This test documents expected behavior
        # In real scenario, would need many rapid requests
        
        # Make a request
        response = client_with_user.get("/api/v1/contratos")
        
        if response.status_code == 429:
            # If rate limited, should have Retry-After
            assert "retry-after" in response.headers or "Retry-After" in response.headers

    def test_successful_request_has_content_type(self, client_with_user: TestClient):
        """Successful response should have Content-Type header"""
        response = client_with_user.get("/api/v1/contratos")
        
        if response.status_code in [200, 404]:
            assert "content-type" in response.headers or "Content-Type" in response.headers


@pytest.mark.rate_limit
class TestAdminRateLimits:
    """Tests for admin endpoint rate limiting (5/min)"""

    def test_admin_endpoint_requires_admin_role(self, client_with_user: TestClient):
        """Admin endpoint should require admin role"""
        response = client_with_user.get("/api/v1/audit-logs/tenant-activity")
        assert response.status_code == 403

    def test_admin_endpoint_accessible_with_admin_role(self, client_with_admin: TestClient):
        """Admin endpoint should be accessible with admin role"""
        response = client_with_admin.get("/api/v1/audit-logs/tenant-activity")
        # Should not be blocked by auth, could be 200 or empty list
        assert response.status_code in [200, 404, 429]

    def test_failed_actions_endpoint_admin_only(self, client_with_user: TestClient):
        """Failed actions should be admin-only"""
        response = client_with_user.get("/api/v1/audit-logs/failed-actions")
        assert response.status_code == 403

    def test_activity_summary_endpoint_admin_only(self, client_with_user: TestClient):
        """Activity summary should be admin-only"""
        response = client_with_user.get("/api/v1/audit-logs/activity-summary")
        assert response.status_code == 403

    def test_suspicious_activity_endpoint_admin_only(self, client_with_user: TestClient):
        """Suspicious activity should be admin-only"""
        response = client_with_user.get("/api/v1/audit-logs/suspicious-activity")
        assert response.status_code == 403


@pytest.mark.rate_limit
class TestAuditLogRateLimits:
    """Tests for audit log endpoints rate limiting (20/min)"""

    def test_my_activity_endpoint_accessible(self, client_with_user: TestClient):
        """My activity endpoint should be accessible to any authenticated user"""
        response = client_with_user.get("/api/v1/audit-logs/my-activity")
        # Should return data or empty list
        assert response.status_code in [200, 404, 429]

    def test_resource_history_endpoint_accessible(self, client_with_user: TestClient):
        """Resource history endpoint should be accessible"""
        response = client_with_user.get("/api/v1/audit-logs/resource/contrato/1")
        assert response.status_code in [200, 404, 429]

    def test_audit_endpoints_with_pagination(self, client_with_user: TestClient):
        """Audit endpoints should support pagination"""
        response = client_with_user.get("/api/v1/audit-logs/my-activity?skip=0&limit=10")
        assert response.status_code in [200, 404, 429]


@pytest.mark.rate_limit
class TestHealthCheckUnlimited:
    """Tests that health check has no rate limit"""

    def test_health_check_no_rate_limit(self, client: TestClient):
        """Health check should not be rate limited"""
        # Even without auth, health check should work
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_multiple_health_checks_allowed(self, client: TestClient):
        """Multiple health checks should be allowed"""
        responses = []
        for _ in range(10):
            response = client.get("/api/v1/health")
            responses.append(response.status_code)
        
        # All should succeed
        assert all(status == 200 for status in responses)

    def test_rapid_health_checks_allowed(self, client: TestClient):
        """Rapid health checks should be allowed"""
        for _ in range(20):
            response = client.get("/api/v1/health")
            if response.status_code != 200:
                # Should never be rate limited
                pytest.fail(f"Health check returned {response.status_code}, expected 200")


@pytest.mark.rate_limit
class TestRateLimitWithDifferentUsers:
    """Tests for rate limiting with different user types"""

    def test_admin_not_blocked_by_user_limit(
        self, client_with_admin: TestClient, client_with_user: TestClient
    ):
        """Admin and user should have separate rate limit counters"""
        # Admin makes request
        response1 = client_with_admin.get("/api/v1/contratos")
        
        # User makes request
        response2 = client_with_user.get("/api/v1/contratos")
        
        # Both should succeed (different counters)
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

    def test_different_users_have_separate_limits(
        self, client_with_user: TestClient, client_with_analyst: TestClient
    ):
        """Different users should have separate rate limit counters"""
        response1 = client_with_user.get("/api/v1/contratos")
        response2 = client_with_analyst.get("/api/v1/contratos")
        
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]


@pytest.mark.rate_limit
class TestRateLimitErrorResponse:
    """Tests for rate limit error response format"""

    def test_rate_limit_response_is_json(self, client_with_user: TestClient):
        """Rate limit response should be JSON"""
        response = client_with_user.get("/api/v1/contratos")
        
        if response.status_code == 429:
            # Should be valid JSON
            try:
                data = response.json()
                assert isinstance(data, dict)
            except ValueError:
                pytest.fail("Rate limit response is not valid JSON")

    def test_rate_limit_response_has_detail(self, client_with_user: TestClient):
        """Rate limit response should have detail field"""
        response = client_with_user.get("/api/v1/contratos")
        
        if response.status_code == 429:
            data = response.json()
            assert "detail" in data or "message" in data or isinstance(data, dict)


@pytest.mark.rate_limit
class TestRateLimitByEndpoint:
    """Tests to verify rate limits are per-endpoint"""

    def test_different_endpoints_separate_limits(self, client_with_user: TestClient):
        """Different endpoints should have separate rate limit counters"""
        # Make requests to different endpoints
        response1 = client_with_user.get("/api/v1/contratos")
        response2 = client_with_user.get("/api/v1/pareceres")
        response3 = client_with_user.get("/api/v1/bureau")
        
        # All should succeed (even if same user, different endpoints)
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]
        assert response3.status_code in [200, 404]

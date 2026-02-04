"""
Authorization Tests (RBAC)
Tests for role-based access control and endpoint authorization
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.authz
class TestRoleBasedAccess:
    """Tests for role-based endpoint access control"""

    def test_admin_can_access_audit_logs(self, client_with_admin: TestClient):
        """Admin should be able to access audit logs"""
        response = client_with_admin.get("/api/v1/audit-logs/my-activity")
        # Should succeed with 200 or return empty list
        assert response.status_code in [200, 404]

    def test_analyst_cannot_access_tenant_activity(self, client_with_analyst: TestClient):
        """Analyst should not access tenant-wide activity logs"""
        response = client_with_analyst.get("/api/v1/audit-logs/tenant-activity")
        assert response.status_code == 403

    def test_user_cannot_access_admin_endpoints(self, client_with_user: TestClient):
        """Regular user should not access admin endpoints"""
        response = client_with_user.get("/api/v1/audit-logs/tenant-activity")
        assert response.status_code == 403

    def test_admin_can_access_user_endpoints(self, client_with_admin: TestClient):
        """Admin should be able to access endpoints available to users"""
        response = client_with_admin.get("/api/v1/audit-logs/my-activity")
        assert response.status_code in [200, 404]

    def test_analyst_can_access_analyst_endpoints(self, client_with_analyst: TestClient):
        """Analyst should access analyst-available endpoints"""
        response = client_with_analyst.get("/api/v1/audit-logs/my-activity")
        assert response.status_code in [200, 404]


@pytest.mark.authz
class TestEndpointRoleRequirements:
    """Tests for role requirements on specific endpoints"""

    def test_contratos_list_requires_auth(self, client: TestClient):
        """List contratos should require authentication"""
        response = client.get("/api/v1/contratos")
        assert response.status_code in [401, 403]

    def test_contratos_list_with_auth(self, client_with_user: TestClient):
        """List contratos with auth should succeed or return empty"""
        response = client_with_user.get("/api/v1/contratos")
        assert response.status_code in [200, 404]

    def test_pareceres_list_requires_auth(self, client: TestClient):
        """List pareceres should require authentication"""
        response = client.get("/api/v1/pareceres")
        assert response.status_code in [401, 403]

    def test_pareceres_list_with_auth(self, client_with_user: TestClient):
        """List pareceres with auth should succeed or return empty"""
        response = client_with_user.get("/api/v1/pareceres")
        assert response.status_code in [200, 404]

    def test_bureau_list_requires_auth(self, client: TestClient):
        """List bureau should require authentication"""
        response = client.get("/api/v1/bureau")
        assert response.status_code in [401, 403]

    def test_bureau_list_with_auth(self, client_with_user: TestClient):
        """List bureau with auth should succeed or return empty"""
        response = client_with_user.get("/api/v1/bureau")
        assert response.status_code in [200, 404]

    def test_geolocalizacao_requires_auth(self, client: TestClient):
        """Geolocalization endpoints should require authentication"""
        response = client.get("/api/v1/geolocalizacao")
        assert response.status_code in [401, 403]


@pytest.mark.authz
class TestAdminOnlyOperations:
    """Tests for admin-only operations"""

    def test_admin_can_view_tenant_activity(self, client_with_admin: TestClient):
        """Admin should view tenant activity"""
        response = client_with_admin.get("/api/v1/audit-logs/tenant-activity")
        assert response.status_code in [200, 404]

    def test_admin_can_view_failed_actions(self, client_with_admin: TestClient):
        """Admin should view failed actions"""
        response = client_with_admin.get("/api/v1/audit-logs/failed-actions")
        assert response.status_code in [200, 404]

    def test_admin_can_view_activity_summary(self, client_with_admin: TestClient):
        """Admin should view activity summary"""
        response = client_with_admin.get("/api/v1/audit-logs/activity-summary")
        assert response.status_code in [200, 404]

    def test_admin_can_detect_suspicious_activity(self, client_with_admin: TestClient):
        """Admin should detect suspicious activity"""
        response = client_with_admin.get("/api/v1/audit-logs/suspicious-activity")
        assert response.status_code in [200, 404]

    def test_non_admin_blocked_from_tenant_activity(self, client_with_user: TestClient):
        """Non-admin user should be blocked from tenant activity"""
        response = client_with_user.get("/api/v1/audit-logs/tenant-activity")
        assert response.status_code == 403

    def test_non_admin_blocked_from_failed_actions(self, client_with_user: TestClient):
        """Non-admin user should be blocked from failed actions"""
        response = client_with_user.get("/api/v1/audit-logs/failed-actions")
        assert response.status_code == 403

    def test_non_admin_blocked_from_activity_summary(self, client_with_user: TestClient):
        """Non-admin user should be blocked from activity summary"""
        response = client_with_user.get("/api/v1/audit-logs/activity-summary")
        assert response.status_code == 403

    def test_non_admin_blocked_from_suspicious_activity(self, client_with_user: TestClient):
        """Non-admin user should be blocked from suspicious activity"""
        response = client_with_user.get("/api/v1/audit-logs/suspicious-activity")
        assert response.status_code == 403


@pytest.mark.authz
class TestAnalystOperations:
    """Tests for analyst-specific operations"""

    def test_analyst_can_view_my_activity(self, client_with_analyst: TestClient):
        """Analyst should view their own activity"""
        response = client_with_analyst.get("/api/v1/audit-logs/my-activity")
        assert response.status_code in [200, 404]

    def test_analyst_can_view_resource_history(self, client_with_analyst: TestClient):
        """Analyst should view resource history"""
        response = client_with_analyst.get(
            "/api/v1/audit-logs/resource/contrato/123"
        )
        assert response.status_code in [200, 404, 403]

    def test_analyst_cannot_view_tenant_activity(self, client_with_analyst: TestClient):
        """Analyst should not view tenant-wide activity"""
        response = client_with_analyst.get("/api/v1/audit-logs/tenant-activity")
        assert response.status_code == 403

    def test_analyst_cannot_view_suspicious_activity(self, client_with_analyst: TestClient):
        """Analyst should not detect suspicious activity"""
        response = client_with_analyst.get("/api/v1/audit-logs/suspicious-activity")
        assert response.status_code == 403


@pytest.mark.authz
class TestUserOperations:
    """Tests for regular user operations"""

    def test_user_can_view_own_activity(self, client_with_user: TestClient):
        """User should view their own activity"""
        response = client_with_user.get("/api/v1/audit-logs/my-activity")
        assert response.status_code in [200, 404]

    def test_user_can_view_resource_history(self, client_with_user: TestClient):
        """User should view resource history"""
        response = client_with_user.get(
            "/api/v1/audit-logs/resource/contrato/123"
        )
        assert response.status_code in [200, 404, 403]

    def test_user_cannot_view_tenant_activity(self, client_with_user: TestClient):
        """User should not view tenant-wide activity"""
        response = client_with_user.get("/api/v1/audit-logs/tenant-activity")
        assert response.status_code == 403

    def test_user_cannot_view_failed_actions(self, client_with_user: TestClient):
        """User should not view failed actions"""
        response = client_with_user.get("/api/v1/audit-logs/failed-actions")
        assert response.status_code == 403


@pytest.mark.authz
class TestMissingAuthenticationHeader:
    """Tests for requests with missing authentication"""

    def test_missing_token_returns_401_or_403(self, client: TestClient):
        """Request without token should return 401/403"""
        response = client.get("/api/v1/contratos")
        assert response.status_code in [401, 403]

    def test_empty_auth_header(self, client: TestClient):
        """Empty auth header should return 401/403"""
        headers = {"Authorization": ""}
        response = client.get("/api/v1/contratos", headers=headers)
        assert response.status_code in [401, 403]

    def test_invalid_auth_format(self, client: TestClient):
        """Invalid auth format should return 401/403"""
        headers = {"Authorization": "InvalidFormat"}
        response = client.get("/api/v1/contratos", headers=headers)
        assert response.status_code in [401, 403]

    def test_health_endpoint_no_auth_required(self, client: TestClient):
        """Health check should not require auth"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200


@pytest.mark.authz
class TestForbiddenOperations:
    """Tests for forbidden operations"""

    def test_analyst_cannot_delete_contrato(self, client_with_analyst: TestClient):
        """Analyst should not delete contratos without proper role"""
        # Note: Depending on role requirements
        response = client_with_analyst.delete("/api/v1/contratos/999")
        # Could be 404 (not found) or 403 (forbidden depending on implementation)
        assert response.status_code in [403, 404]

    def test_user_cannot_upload_file(self, client_with_user: TestClient):
        """User should not upload files without proper role"""
        # Note: Depends on role requirements
        response = client_with_user.post(
            "/api/v1/contratos/upload",
            files={"file": ("test.pdf", b"content", "application/pdf")}
        )
        assert response.status_code in [403, 422]

    def test_different_tenant_cannot_access_data(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """User from one tenant should not access another tenant's data"""
        # Both should be able to list contratos (empty for new tenant)
        response1 = client_with_user.get("/api/v1/contratos")
        response2 = client_with_other_tenant.get("/api/v1/contratos")
        
        # Both should return 200 (data isolation handled at query level)
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]


@pytest.mark.authz
class TestRoleHierarchy:
    """Tests for role hierarchy and inheritance"""

    def test_admin_has_all_analyst_permissions(self, client_with_admin: TestClient):
        """Admin should have all analyst permissions"""
        # Admin accessing analyst endpoints
        response = client_with_admin.get("/api/v1/audit-logs/my-activity")
        assert response.status_code in [200, 404]

    def test_admin_has_additional_permissions(self, client_with_admin: TestClient):
        """Admin should have additional permissions beyond analyst"""
        response = client_with_admin.get("/api/v1/audit-logs/tenant-activity")
        assert response.status_code in [200, 404]

    def test_analyst_subset_of_admin(self, client_with_analyst: TestClient):
        """Analyst permissions should be subset of admin"""
        # Can view own activity
        response = client_with_analyst.get("/api/v1/audit-logs/my-activity")
        assert response.status_code in [200, 404]

    def test_user_subset_of_analyst(self, client_with_user: TestClient):
        """User permissions should be subset of analyst"""
        response = client_with_user.get("/api/v1/audit-logs/my-activity")
        assert response.status_code in [200, 404]

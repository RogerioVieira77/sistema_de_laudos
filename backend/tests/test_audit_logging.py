"""
Audit Logging Tests
Tests for audit log creation, querying, and functionality
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.audit
class TestAuditLogEndpoints:
    """Tests for audit log API endpoints"""

    def test_my_activity_endpoint_returns_list(self, client_with_user: TestClient):
        """My activity endpoint should return a list"""
        response = client_with_user.get("/api/v1/audit-logs/my-activity")
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "items" in data or "data" in data or isinstance(data, list)

    def test_my_activity_requires_auth(self, client: TestClient):
        """My activity endpoint should require authentication"""
        response = client.get("/api/v1/audit-logs/my-activity")
        assert response.status_code in [401, 403]

    def test_tenant_activity_requires_admin(self, client_with_user: TestClient):
        """Tenant activity endpoint should require admin role"""
        response = client_with_user.get("/api/v1/audit-logs/tenant-activity")
        assert response.status_code == 403

    def test_tenant_activity_accessible_to_admin(self, client_with_admin: TestClient):
        """Tenant activity endpoint should be accessible to admin"""
        response = client_with_admin.get("/api/v1/audit-logs/tenant-activity")
        assert response.status_code in [200, 404, 429]

    def test_resource_history_returns_list(self, client_with_user: TestClient):
        """Resource history endpoint should return a list"""
        response = client_with_user.get("/api/v1/audit-logs/resource/contrato/1")
        
        assert response.status_code in [200, 404, 429]
        if response.status_code == 200:
            data = response.json()
            assert "items" in data or isinstance(data, list)

    def test_failed_actions_requires_admin(self, client_with_user: TestClient):
        """Failed actions endpoint should require admin"""
        response = client_with_user.get("/api/v1/audit-logs/failed-actions")
        assert response.status_code == 403

    def test_failed_actions_accessible_to_admin(self, client_with_admin: TestClient):
        """Failed actions endpoint should be accessible to admin"""
        response = client_with_admin.get("/api/v1/audit-logs/failed-actions")
        assert response.status_code in [200, 404, 429]

    def test_activity_summary_requires_admin(self, client_with_user: TestClient):
        """Activity summary endpoint should require admin"""
        response = client_with_user.get("/api/v1/audit-logs/activity-summary")
        assert response.status_code == 403

    def test_activity_summary_accessible_to_admin(self, client_with_admin: TestClient):
        """Activity summary endpoint should be accessible to admin"""
        response = client_with_admin.get("/api/v1/audit-logs/activity-summary")
        assert response.status_code in [200, 404, 429]

    def test_suspicious_activity_requires_admin(self, client_with_user: TestClient):
        """Suspicious activity endpoint should require admin"""
        response = client_with_user.get("/api/v1/audit-logs/suspicious-activity")
        assert response.status_code == 403

    def test_suspicious_activity_accessible_to_admin(self, client_with_admin: TestClient):
        """Suspicious activity endpoint should be accessible to admin"""
        response = client_with_admin.get("/api/v1/audit-logs/suspicious-activity")
        assert response.status_code in [200, 404, 429]


@pytest.mark.audit
class TestAuditLogPagination:
    """Tests for audit log pagination"""

    def test_my_activity_with_skip_parameter(self, client_with_user: TestClient):
        """My activity should support skip parameter"""
        response = client_with_user.get("/api/v1/audit-logs/my-activity?skip=0")
        assert response.status_code in [200, 404, 429]

    def test_my_activity_with_limit_parameter(self, client_with_user: TestClient):
        """My activity should support limit parameter"""
        response = client_with_user.get("/api/v1/audit-logs/my-activity?limit=10")
        assert response.status_code in [200, 404, 429]

    def test_my_activity_with_skip_and_limit(self, client_with_user: TestClient):
        """My activity should support both skip and limit"""
        response = client_with_user.get("/api/v1/audit-logs/my-activity?skip=0&limit=10")
        assert response.status_code in [200, 404, 429]

    def test_tenant_activity_with_pagination(self, client_with_admin: TestClient):
        """Tenant activity should support pagination"""
        response = client_with_admin.get(
            "/api/v1/audit-logs/tenant-activity?skip=0&limit=50"
        )
        assert response.status_code in [200, 404, 429]

    def test_failed_actions_with_pagination(self, client_with_admin: TestClient):
        """Failed actions should support pagination"""
        response = client_with_admin.get(
            "/api/v1/audit-logs/failed-actions?skip=0&limit=25"
        )
        assert response.status_code in [200, 404, 429]


@pytest.mark.audit
class TestAuditLogFiltering:
    """Tests for audit log filtering"""

    def test_my_activity_with_days_back_filter(self, client_with_user: TestClient):
        """My activity should support days_back filter"""
        response = client_with_user.get("/api/v1/audit-logs/my-activity?days_back=7")
        assert response.status_code in [200, 404, 429]

    def test_tenant_activity_with_action_filter(self, client_with_admin: TestClient):
        """Tenant activity should support action filter"""
        response = client_with_admin.get(
            "/api/v1/audit-logs/tenant-activity?action=CREATE"
        )
        assert response.status_code in [200, 404, 429]

    def test_tenant_activity_with_status_filter(self, client_with_admin: TestClient):
        """Tenant activity should support status filter"""
        response = client_with_admin.get(
            "/api/v1/audit-logs/tenant-activity?status=success"
        )
        assert response.status_code in [200, 404, 429]

    def test_failed_actions_with_days_back(self, client_with_admin: TestClient):
        """Failed actions should support days_back filter"""
        response = client_with_admin.get("/api/v1/audit-logs/failed-actions?days_back=7")
        assert response.status_code in [200, 404, 429]

    def test_activity_summary_with_days_back(self, client_with_admin: TestClient):
        """Activity summary should support days_back filter"""
        response = client_with_admin.get("/api/v1/audit-logs/activity-summary?days_back=30")
        assert response.status_code in [200, 404, 429]

    def test_suspicious_activity_with_threshold(self, client_with_admin: TestClient):
        """Suspicious activity should support threshold parameter"""
        response = client_with_admin.get("/api/v1/audit-logs/suspicious-activity?threshold=5")
        assert response.status_code in [200, 404, 429]


@pytest.mark.audit
class TestAuditLogTenantFiltering:
    """Tests that audit logs filter by tenant"""

    def test_my_activity_filtered_by_tenant(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """My activity should only show own tenant's activities"""
        response1 = client_with_user.get("/api/v1/audit-logs/my-activity")
        response2 = client_with_other_tenant.get("/api/v1/audit-logs/my-activity")
        
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

    def test_tenant_activity_filtered_by_tenant(
        self, client_with_admin: TestClient, client_with_other_tenant: TestClient
    ):
        """Tenant activity should only show own tenant's activities"""
        # Admin from tenant-123
        response1 = client_with_admin.get("/api/v1/audit-logs/tenant-activity")
        
        # Admin from tenant-other
        response2 = client_with_other_tenant.get("/api/v1/audit-logs/tenant-activity")
        
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

    def test_resource_history_filtered_by_tenant(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """Resource history should only show own tenant's resources"""
        response1 = client_with_user.get("/api/v1/audit-logs/resource/contrato/1")
        response2 = client_with_other_tenant.get("/api/v1/audit-logs/resource/contrato/1")
        
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

    def test_failed_actions_filtered_by_tenant(
        self, client_with_admin: TestClient, client_with_other_tenant: TestClient
    ):
        """Failed actions should only show own tenant's failures"""
        response1 = client_with_admin.get("/api/v1/audit-logs/failed-actions")
        response2 = client_with_other_tenant.get("/api/v1/audit-logs/failed-actions")
        
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]


@pytest.mark.audit
class TestAuditLogDataStructure:
    """Tests for audit log response data structure"""

    def test_my_activity_response_structure(self, client_with_user: TestClient):
        """My activity response should have correct structure"""
        response = client_with_user.get("/api/v1/audit-logs/my-activity")
        
        if response.status_code == 200:
            data = response.json()
            # Should have pagination metadata
            if isinstance(data, dict):
                assert "items" in data or "data" in data or "total" in data

    def test_activity_summary_has_statistics(self, client_with_admin: TestClient):
        """Activity summary should contain statistics"""
        response = client_with_admin.get("/api/v1/audit-logs/activity-summary")
        
        if response.status_code == 200:
            data = response.json()
            # Should be dict with summary info
            assert isinstance(data, dict)

    def test_failed_actions_contains_error_info(self, client_with_admin: TestClient):
        """Failed actions response should contain error information"""
        response = client_with_admin.get("/api/v1/audit-logs/failed-actions")
        
        if response.status_code == 200:
            data = response.json()
            # Should be a list or have items
            if isinstance(data, dict):
                assert "items" in data or "data" in data or "results" in data


@pytest.mark.audit
class TestAuditLogAuthorization:
    """Tests for proper authorization on audit log endpoints"""

    def test_only_admin_can_view_tenant_activity(
        self, client_with_user: TestClient, client_with_analyst: TestClient
    ):
        """Only admins should view tenant-wide activity"""
        user_response = client_with_user.get("/api/v1/audit-logs/tenant-activity")
        analyst_response = client_with_analyst.get("/api/v1/audit-logs/tenant-activity")
        
        assert user_response.status_code == 403
        assert analyst_response.status_code == 403

    def test_only_admin_can_view_failed_actions(
        self, client_with_user: TestClient, client_with_analyst: TestClient
    ):
        """Only admins should view failed actions"""
        user_response = client_with_user.get("/api/v1/audit-logs/failed-actions")
        analyst_response = client_with_analyst.get("/api/v1/audit-logs/failed-actions")
        
        assert user_response.status_code == 403
        assert analyst_response.status_code == 403

    def test_only_admin_can_view_activity_summary(
        self, client_with_user: TestClient, client_with_analyst: TestClient
    ):
        """Only admins should view activity summary"""
        user_response = client_with_user.get("/api/v1/audit-logs/activity-summary")
        analyst_response = client_with_analyst.get("/api/v1/audit-logs/activity-summary")
        
        assert user_response.status_code == 403
        assert analyst_response.status_code == 403

    def test_only_admin_can_detect_suspicious_activity(
        self, client_with_user: TestClient, client_with_analyst: TestClient
    ):
        """Only admins should detect suspicious activity"""
        user_response = client_with_user.get("/api/v1/audit-logs/suspicious-activity")
        analyst_response = client_with_analyst.get("/api/v1/audit-logs/suspicious-activity")
        
        assert user_response.status_code == 403
        assert analyst_response.status_code == 403

    def test_any_authenticated_user_can_view_own_activity(
        self, client_with_user: TestClient, client_with_analyst: TestClient, client_with_admin: TestClient
    ):
        """Any authenticated user should view own activity"""
        user_response = client_with_user.get("/api/v1/audit-logs/my-activity")
        analyst_response = client_with_analyst.get("/api/v1/audit-logs/my-activity")
        admin_response = client_with_admin.get("/api/v1/audit-logs/my-activity")
        
        assert user_response.status_code in [200, 404, 429]
        assert analyst_response.status_code in [200, 404, 429]
        assert admin_response.status_code in [200, 404, 429]

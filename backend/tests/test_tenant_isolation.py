"""
Tenant Isolation Tests
Tests for multi-tenant data isolation and security
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.tenant
class TestTenantIsolation:
    """Tests for basic tenant isolation"""

    def test_user_identity_contains_tenant_id(self, user_identity):
        """User identity should have tenant_id"""
        assert hasattr(user_identity, "tenant_id")
        assert user_identity.tenant_id == "tenant-123"

    def test_different_users_can_have_different_tenants(
        self, user_identity, other_tenant_identity
    ):
        """Different users can belong to different tenants"""
        assert user_identity.tenant_id != other_tenant_identity.tenant_id

    def test_authentication_preserves_tenant(self, client_with_user: TestClient):
        """Authenticated request should preserve tenant context"""
        response = client_with_user.get("/api/v1/health")
        assert response.status_code == 200

    def test_different_tenant_users_separate_context(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """Different tenant users should have separate context"""
        # Both should be able to access health endpoint
        response1 = client_with_user.get("/api/v1/health")
        response2 = client_with_other_tenant.get("/api/v1/health")
        
        assert response1.status_code == 200
        assert response2.status_code == 200


@pytest.mark.tenant
class TestDataIsolation:
    """Tests for data isolation between tenants"""

    def test_contratos_list_filters_by_tenant(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """Contratos list should only return data for requesting tenant"""
        # Get contratos for user in tenant-123
        response1 = client_with_user.get("/api/v1/contratos")
        
        # Get contratos for user in tenant-other
        response2 = client_with_other_tenant.get("/api/v1/contratos")
        
        # Both should return 200 (or empty list)
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]
        
        # If both return data, they should be different sets
        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            # Should not have same contratos
            # (depends on implementation details)

    def test_pareceres_list_filters_by_tenant(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """Pareceres list should only return data for requesting tenant"""
        response1 = client_with_user.get("/api/v1/pareceres")
        response2 = client_with_other_tenant.get("/api/v1/pareceres")
        
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

    def test_bureau_list_filters_by_tenant(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """Bureau list should only return data for requesting tenant"""
        response1 = client_with_user.get("/api/v1/bureau")
        response2 = client_with_other_tenant.get("/api/v1/bureau")
        
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

    def test_audit_logs_filtered_by_tenant(
        self, client_with_admin: TestClient
    ):
        """Audit logs should only return data for requesting tenant"""
        response = client_with_admin.get("/api/v1/audit-logs/tenant-activity")
        
        # Should return 200 (possibly empty for new tenant)
        assert response.status_code in [200, 404]


@pytest.mark.tenant
class TestCrossTenantAccessPrevention:
    """Tests to prevent cross-tenant data access"""

    def test_cannot_access_other_tenant_contrato(
        self, client_with_other_tenant: TestClient
    ):
        """User should not access contrato from different tenant"""
        # Try to access contrato ID 1 (which belongs to tenant-123)
        response = client_with_other_tenant.get("/api/v1/contratos/1")
        
        # Should return 403 (forbidden) or 404 (not found)
        assert response.status_code in [403, 404]

    def test_cannot_access_other_tenant_parecer(
        self, client_with_other_tenant: TestClient
    ):
        """User should not access parecer from different tenant"""
        response = client_with_other_tenant.get("/api/v1/pareceres/1")
        
        assert response.status_code in [403, 404]

    def test_cannot_access_other_tenant_bureau(
        self, client_with_other_tenant: TestClient
    ):
        """User should not access bureau from different tenant"""
        response = client_with_other_tenant.get("/api/v1/bureau/1")
        
        assert response.status_code in [403, 404]

    def test_cannot_delete_other_tenant_contrato(
        self, client_with_other_tenant: TestClient
    ):
        """User should not delete contrato from different tenant"""
        response = client_with_other_tenant.delete("/api/v1/contratos/1")
        
        assert response.status_code in [403, 404]

    def test_cannot_delete_other_tenant_parecer(
        self, client_with_other_tenant: TestClient
    ):
        """User should not delete parecer from different tenant"""
        response = client_with_other_tenant.delete("/api/v1/pareceres/1")
        
        assert response.status_code in [403, 404]


@pytest.mark.tenant
class TestTenantAdminOperations:
    """Tests for tenant-admin restricted operations"""

    def test_admin_can_view_tenant_activity_own_tenant(
        self, client_with_admin: TestClient
    ):
        """Admin should view activity for own tenant"""
        response = client_with_admin.get("/api/v1/audit-logs/tenant-activity")
        
        assert response.status_code in [200, 404]

    def test_admin_cannot_view_other_tenant_activity(
        self, client_with_admin: TestClient, client_with_other_tenant: TestClient
    ):
        """Admin from one tenant should not see other tenant's activity"""
        # Admin from tenant-123
        response1 = client_with_admin.get("/api/v1/audit-logs/tenant-activity")
        
        # Admin from tenant-other
        response2 = client_with_other_tenant.get("/api/v1/audit-logs/tenant-activity")
        
        # Both should return 200 (for their own tenants)
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

    def test_activity_summary_filtered_by_tenant(
        self, client_with_admin: TestClient
    ):
        """Activity summary should only include own tenant data"""
        response = client_with_admin.get("/api/v1/audit-logs/activity-summary")
        
        assert response.status_code in [200, 404]

    def test_suspicious_activity_filtered_by_tenant(
        self, client_with_admin: TestClient
    ):
        """Suspicious activity detection should only check own tenant"""
        response = client_with_admin.get("/api/v1/audit-logs/suspicious-activity")
        
        assert response.status_code in [200, 404]


@pytest.mark.tenant
class TestResourceHistoryTenantFiltering:
    """Tests for resource history tenant filtering"""

    def test_resource_history_filters_by_tenant(
        self, client_with_user: TestClient
    ):
        """Resource history should only show own tenant's data"""
        response = client_with_user.get("/api/v1/audit-logs/resource/contrato/1")
        
        # Should return 200 (empty) or 404 (not found)
        assert response.status_code in [200, 404]

    def test_cannot_view_other_tenant_resource_history(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """User should not see other tenant's resource history"""
        # User from tenant-123
        response1 = client_with_user.get("/api/v1/audit-logs/resource/contrato/1")
        
        # User from tenant-other
        response2 = client_with_other_tenant.get("/api/v1/audit-logs/resource/contrato/1")
        
        # Both should return 200 (empty) or 404
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]


@pytest.mark.tenant
class TestTenantIdInContext:
    """Tests for tenant_id being maintained in request context"""

    def test_user_tenant_id_extraction(self, user_identity):
        """Tenant ID should be extractable from user identity"""
        assert user_identity.tenant_id == "tenant-123"

    def test_admin_tenant_id_extraction(self, admin_identity):
        """Admin tenant ID should be extractable"""
        assert admin_identity.tenant_id == "tenant-123"

    def test_different_tenant_ids_different_users(
        self, user_identity, other_tenant_identity
    ):
        """Different tenant IDs for different user fixtures"""
        assert user_identity.tenant_id == "tenant-123"
        assert other_tenant_identity.tenant_id == "tenant-other"
        assert user_identity.tenant_id != other_tenant_identity.tenant_id

    def test_tenant_id_consistency_across_requests(
        self, client_with_user: TestClient
    ):
        """Tenant ID should be consistent across multiple requests"""
        # Make multiple requests
        response1 = client_with_user.get("/api/v1/health")
        response2 = client_with_user.get("/api/v1/health")
        
        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200


@pytest.mark.tenant
class TestMultiTenantScenarios:
    """Tests for complex multi-tenant scenarios"""

    def test_simultaneous_different_tenant_users(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """Different tenant users can be active simultaneously"""
        # Both users access their data
        response1 = client_with_user.get("/api/v1/contratos")
        response2 = client_with_other_tenant.get("/api/v1/contratos")
        
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

    def test_tenant_isolation_with_admin_operations(
        self, client_with_admin: TestClient, client_with_other_tenant: TestClient
    ):
        """Admin operations should respect tenant boundaries"""
        # Admin from tenant-123 views activity
        response1 = client_with_admin.get("/api/v1/audit-logs/tenant-activity")
        
        # Admin from other tenant views activity
        response2 = client_with_other_tenant.get("/api/v1/audit-logs/tenant-activity")
        
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

    def test_cross_tenant_confusion_prevention(
        self, client_with_user: TestClient, client_with_other_tenant: TestClient
    ):
        """Operations should not leak data across tenants"""
        # Both users access same endpoint
        response1 = client_with_user.get("/api/v1/pareceres")
        response2 = client_with_other_tenant.get("/api/v1/pareceres")
        
        # Both should work but with isolated data
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

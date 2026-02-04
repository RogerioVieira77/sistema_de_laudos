"""
Testes para modelos (Tenant, AuditLog, Usuario)
"""

import pytest
from datetime import datetime
from app.models import Tenant, AuditLog, AuditAction, AuditStatus, Usuario


class TestTenant:
    """Testes para o modelo Tenant"""
    
    def test_create_tenant(self):
        """Testar criação de tenant"""
        tenant = Tenant(
            name="Empresa Teste",
            description="Tenant para testes",
            active=True,
        )
        
        assert tenant.name == "Empresa Teste"
        assert tenant.description == "Tenant para testes"
        assert tenant.active is True
        assert tenant.id is not None
    
    def test_tenant_default_values(self):
        """Testar valores padrão do tenant"""
        tenant = Tenant(name="Test Tenant")
        
        assert tenant.active is True
        assert tenant.created_at is not None
        assert tenant.updated_at is not None
        assert isinstance(tenant.created_at, datetime)
    
    def test_tenant_to_dict(self):
        """Testar conversão para dicionário"""
        tenant = Tenant(
            name="Empresa Teste",
            description="Descrição",
            active=True,
        )
        
        tenant_dict = tenant.to_dict()
        
        assert tenant_dict["name"] == "Empresa Teste"
        assert tenant_dict["description"] == "Descrição"
        assert tenant_dict["active"] is True
        assert "id" in tenant_dict
        assert "created_at" in tenant_dict
    
    def test_tenant_create_default(self):
        """Testar criação de tenant padrão"""
        default_tenant = Tenant.create_default()
        
        assert default_tenant.id == "default"
        assert default_tenant.name == "Default Tenant"
        assert default_tenant.active is True
    
    def test_tenant_repr(self):
        """Testar representação do tenant"""
        tenant = Tenant(id="test-123", name="Test Tenant", active=True)
        repr_str = repr(tenant)
        
        assert "Tenant" in repr_str
        assert "test-123" in repr_str
        assert "Test Tenant" in repr_str


class TestAuditLog:
    """Testes para o modelo AuditLog"""
    
    def test_create_audit_log(self):
        """Testar criação de log de auditoria"""
        log = AuditLog(
            user_id="user-123",
            user_email="user@example.com",
            action=AuditAction.CREATE,
            resource_type="contrato",
            resource_id="resource-456",
            tenant_id="tenant-789",
            status=AuditStatus.SUCCESS,
        )
        
        assert log.user_id == "user-123"
        assert log.user_email == "user@example.com"
        assert log.action == AuditAction.CREATE
        assert log.resource_type == "contrato"
        assert log.status == AuditStatus.SUCCESS
        assert log.id is not None
    
    def test_audit_log_default_values(self):
        """Testar valores padrão do log"""
        log = AuditLog(
            user_id="user-123",
            user_email="user@example.com",
            action=AuditAction.READ,
            resource_type="parecer",
        )
        
        assert log.tenant_id == "default"
        assert log.status == AuditStatus.SUCCESS
        assert log.error_message is None
        assert log.timestamp is not None
        assert isinstance(log.timestamp, datetime)
    
    def test_audit_action_enum(self):
        """Testar enum de ações"""
        actions = [
            AuditAction.CREATE,
            AuditAction.READ,
            AuditAction.UPDATE,
            AuditAction.DELETE,
            AuditAction.EXPORT,
            AuditAction.DOWNLOAD,
            AuditAction.UPLOAD,
            AuditAction.LOGIN,
        ]
        
        assert len(actions) == 8
        assert AuditAction.CREATE.value == "CREATE"
        assert AuditAction.DELETE.value == "DELETE"
    
    def test_audit_status_enum(self):
        """Testar enum de status"""
        statuses = [
            AuditStatus.SUCCESS,
            AuditStatus.ERROR,
            AuditStatus.BLOCKED,
        ]
        
        assert len(statuses) == 3
        assert AuditStatus.SUCCESS.value == "success"
        assert AuditStatus.BLOCKED.value == "blocked"
    
    def test_audit_log_factory_method(self):
        """Testar factory method log_action"""
        log = AuditLog.log_action(
            user_id="user-123",
            user_email="user@example.com",
            action=AuditAction.DELETE,
            resource_type="contrato",
            resource_id="contract-456",
            tenant_id="tenant-789",
            status=AuditStatus.SUCCESS,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0...",
            details={"reason": "obsoleto"},
        )
        
        assert log.user_id == "user-123"
        assert log.action == AuditAction.DELETE
        assert log.details == {"reason": "obsoleto"}
        assert log.ip_address == "192.168.1.100"
    
    def test_audit_log_with_error(self):
        """Testar log com erro"""
        log = AuditLog(
            user_id="user-123",
            user_email="user@example.com",
            action=AuditAction.EXPORT,
            resource_type="bureau",
            status=AuditStatus.ERROR,
            error_message="Acesso negado: role insuficiente",
        )
        
        assert log.status == AuditStatus.ERROR
        assert log.error_message == "Acesso negado: role insuficiente"
    
    def test_audit_log_to_dict(self):
        """Testar conversão para dicionário"""
        log = AuditLog(
            user_id="user-123",
            user_email="user@example.com",
            action=AuditAction.CREATE,
            resource_type="parecer",
            resource_id="parecer-456",
            tenant_id="tenant-789",
            status=AuditStatus.SUCCESS,
            details={"version": 1},
        )
        
        log_dict = log.to_dict()
        
        assert log_dict["user_id"] == "user-123"
        assert log_dict["user_email"] == "user@example.com"
        assert log_dict["action"] == "CREATE"
        assert log_dict["resource_type"] == "parecer"
        assert log_dict["status"] == "success"
        assert log_dict["details"] == {"version": 1}
    
    def test_audit_log_repr(self):
        """Testar representação do log"""
        log = AuditLog(
            user_id="user-123",
            user_email="user@example.com",
            action=AuditAction.UPDATE,
            resource_type="contrato",
            status=AuditStatus.SUCCESS,
        )
        
        repr_str = repr(log)
        assert "AuditLog" in repr_str
        assert "UPDATE" in repr_str
        assert "contrato" in repr_str


class TestUsuarioExtension:
    """Testes para extensão do modelo Usuario com tenant_id"""
    
    def test_usuario_with_tenant_id(self):
        """Testar usuario com tenant_id"""
        usuario = Usuario(
            keycloak_id="keycloak-123",
            email="user@example.com",
            nome="João Silva",
            cargo="Analista",
            tenant_id="tenant-456",
            ativo=True,
        )
        
        assert usuario.tenant_id == "tenant-456"
        assert usuario.keycloak_id == "keycloak-123"
        assert usuario.email == "user@example.com"
    
    def test_usuario_default_tenant_id(self):
        """Testar valor padrão de tenant_id"""
        usuario = Usuario(
            keycloak_id="keycloak-123",
            email="user@example.com",
            nome="João Silva",
        )
        
        assert usuario.tenant_id == "default"
    
    def test_usuario_to_dict(self):
        """Testar conversão para dicionário"""
        usuario = Usuario(
            keycloak_id="keycloak-123",
            email="user@example.com",
            nome="João Silva",
            cargo="Analista",
            tenant_id="tenant-456",
        )
        
        usuario_dict = usuario.to_dict()
        
        assert usuario_dict["email"] == "user@example.com"
        assert usuario_dict["nome"] == "João Silva"
        assert usuario_dict["tenant_id"] == "tenant-456"
        assert usuario_dict["cargo"] == "Analista"
    
    def test_usuario_repr_with_tenant(self):
        """Testar representação com tenant_id"""
        usuario = Usuario(
            keycloak_id="keycloak-123",
            email="user@example.com",
            nome="João Silva",
            tenant_id="tenant-456",
        )
        
        repr_str = repr(usuario)
        assert "usuario@example.com" in repr_str or "user@example.com" in repr_str
        assert "tenant-456" in repr_str


class TestMultiTenancy:
    """Testes para isolação multi-tenant"""
    
    def test_multiple_tenants_isolation(self):
        """Testar isolação de tenants diferentes"""
        tenant1 = Tenant(id="tenant-1", name="Empresa A")
        tenant2 = Tenant(id="tenant-2", name="Empresa B")
        
        assert tenant1.id != tenant2.id
        assert tenant1.name != tenant2.name
    
    def test_audit_logs_per_tenant(self):
        """Testar logs de auditoria por tenant"""
        log1 = AuditLog.log_action(
            user_id="user-1",
            user_email="user1@example.com",
            action=AuditAction.CREATE,
            resource_type="contrato",
            tenant_id="tenant-1",
        )
        
        log2 = AuditLog.log_action(
            user_id="user-2",
            user_email="user2@example.com",
            action=AuditAction.CREATE,
            resource_type="contrato",
            tenant_id="tenant-2",
        )
        
        assert log1.tenant_id == "tenant-1"
        assert log2.tenant_id == "tenant-2"
        assert log1.user_id != log2.user_id
    
    def test_usuarios_per_tenant(self):
        """Testar usuários por tenant"""
        usuario1 = Usuario(
            keycloak_id="user-1",
            email="user1@example.com",
            nome="User 1",
            tenant_id="tenant-1",
        )
        
        usuario2 = Usuario(
            keycloak_id="user-2",
            email="user2@example.com",
            nome="User 2",
            tenant_id="tenant-2",
        )
        
        assert usuario1.tenant_id == "tenant-1"
        assert usuario2.tenant_id == "tenant-2"

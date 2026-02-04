"""
Create audit_logs table

Revision ID: 002_audit_logs
Revises: 001_initial_migration
Create Date: 2024-02-03 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_audit_logs'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tipo ENUM para AuditAction
    audit_action_enum = postgresql.ENUM(
        'CREATE', 'READ', 'UPDATE', 'DELETE', 'EXPORT', 'DOWNLOAD', 'UPLOAD', 'EXECUTE', 'LOGIN', 'LOGOUT',
        name='auditaction',
        create_type=True
    )
    audit_action_enum.create(op.get_bind(), checkfirst=True)
    
    # Criar tipo ENUM para AuditStatus
    audit_status_enum = postgresql.ENUM(
        'success', 'error', 'blocked',
        name='auditstatus',
        create_type=True
    )
    audit_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Criar tabela audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('action', postgresql.ENUM('CREATE', 'READ', 'UPDATE', 'DELETE', 'EXPORT', 'DOWNLOAD', 'UPLOAD', 'EXECUTE', 'LOGIN', 'LOGOUT', name='auditaction'), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(36), nullable=True),
        sa.Column('status', postgresql.ENUM('success', 'error', 'blocked', name='auditstatus'), nullable=False),
        sa.Column('error_message', sa.String(500), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('details', postgresql.JSON, nullable=True),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_user_email', 'audit_logs', ['user_email'])
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('ix_audit_logs_resource_id', 'audit_logs', ['resource_id'])
    op.create_index('ix_audit_logs_status', 'audit_logs', ['status'])
    op.create_index('ix_audit_logs_ip_address', 'audit_logs', ['ip_address'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    
    # Índices compostos para queries comuns
    op.create_index(
        'ix_audit_logs_tenant_action_timestamp',
        'audit_logs',
        ['tenant_id', 'action', 'timestamp']
    )
    op.create_index(
        'ix_audit_logs_user_timestamp',
        'audit_logs',
        ['user_id', 'timestamp']
    )
    op.create_index(
        'ix_audit_logs_resource',
        'audit_logs',
        ['resource_type', 'resource_id']
    )
    op.create_index(
        'ix_audit_logs_timestamp_cleanup',
        'audit_logs',
        ['timestamp']
    )


def downgrade():
    # Remover índices
    op.drop_index('ix_audit_logs_timestamp_cleanup')
    op.drop_index('ix_audit_logs_resource')
    op.drop_index('ix_audit_logs_user_timestamp')
    op.drop_index('ix_audit_logs_tenant_action_timestamp')
    op.drop_index('ix_audit_logs_timestamp')
    op.drop_index('ix_audit_logs_ip_address')
    op.drop_index('ix_audit_logs_status')
    op.drop_index('ix_audit_logs_resource_id')
    op.drop_index('ix_audit_logs_resource_type')
    op.drop_index('ix_audit_logs_action')
    op.drop_index('ix_audit_logs_tenant_id')
    op.drop_index('ix_audit_logs_user_email')
    op.drop_index('ix_audit_logs_user_id')
    
    # Remover tabela
    op.drop_table('audit_logs')
    
    # Remover ENUMs
    audit_status_enum = postgresql.ENUM('success', 'error', 'blocked', name='auditstatus')
    audit_status_enum.drop(op.get_bind(), checkfirst=True)
    
    audit_action_enum = postgresql.ENUM('CREATE', 'READ', 'UPDATE', 'DELETE', 'EXPORT', 'DOWNLOAD', 'UPLOAD', 'EXECUTE', 'LOGIN', 'LOGOUT', name='auditaction')
    audit_action_enum.drop(op.get_bind(), checkfirst=True)

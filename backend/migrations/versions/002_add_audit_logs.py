"""add audit logs table

Revision ID: 002_add_audit_logs
Revises: 001_initial_migration
Create Date: 2024-02-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '002_add_audit_logs'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Criar tabelas de auditoria e tenant"""
    
    # Criar tabela de tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('active', sa.Boolean, nullable=False, default=True),
    )
    
    op.create_index('ix_tenants_id', 'tenants', ['id'])
    op.create_index('ix_tenants_name', 'tenants', ['name'])
    
    # Adicionar coluna tenant_id na tabela usuarios (se existir)
    try:
        op.add_column(
            'usuarios',
            sa.Column('tenant_id', sa.String(36), nullable=True, default='default')
        )
        op.create_index('ix_usuarios_tenant_id', 'usuarios', ['tenant_id'])
    except Exception as e:
        print(f"Aviso: Não foi possível adicionar tenant_id em usuarios: {e}")
    
    # Criar tabela de audit logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        
        # Identificação do usuário
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False, default='default'),
        
        # Ação
        sa.Column('action', sa.String(50), nullable=False),  # CREATE, READ, UPDATE, DELETE, EXPORT, DOWNLOAD
        sa.Column('resource_type', sa.String(100), nullable=False),  # contrato, parecer, bureau, etc
        sa.Column('resource_id', sa.String(36), nullable=True),
        
        # Resultado
        sa.Column('status', sa.String(20), nullable=False, default='success'),  # success, error, blocked
        sa.Column('error_message', sa.String(500), nullable=True),
        
        # Metadados
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('details', sa.Text, nullable=True),  # JSON com detalhes adicionais
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('timestamp', sa.DateTime, nullable=False, default=datetime.utcnow),
    )
    
    # Índices para performance em queries
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'])
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index(
        'ix_audit_logs_tenant_action_timestamp',
        'audit_logs',
        ['tenant_id', 'action', 'timestamp'],
        unique=False
    )
    op.create_index(
        'ix_audit_logs_user_timestamp',
        'audit_logs',
        ['user_id', 'timestamp'],
        unique=False
    )


def downgrade() -> None:
    """Reverter as mudanças"""
    
    # Drop indices
    op.drop_index('ix_audit_logs_user_timestamp', table_name='audit_logs')
    op.drop_index('ix_audit_logs_tenant_action_timestamp', table_name='audit_logs')
    op.drop_index('ix_audit_logs_timestamp', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_resource_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_tenant_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_id', table_name='audit_logs')
    
    # Drop tabela audit_logs
    op.drop_table('audit_logs')
    
    # Remover coluna tenant_id
    try:
        op.drop_index('ix_usuarios_tenant_id', table_name='usuarios')
        op.drop_column('usuarios', 'tenant_id')
    except Exception as e:
        print(f"Aviso: Não foi possível remover tenant_id: {e}")
    
    # Drop índices da tabela tenants
    op.drop_index('ix_tenants_name', table_name='tenants')
    op.drop_index('ix_tenants_id', table_name='tenants')
    
    # Drop tabela tenants
    op.drop_table('tenants')

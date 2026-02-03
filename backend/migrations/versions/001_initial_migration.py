"""Initial migration: create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-03 00:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create usuarios table
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('keycloak_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('cargo', sa.String(length=100), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_usuario_keycloak_id', 'usuarios', ['keycloak_id'], unique=False)
    op.create_index('idx_usuario_email', 'usuarios', ['email'], unique=False)
    op.create_index('idx_usuario_ativo', 'usuarios', ['ativo'], unique=False)
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)
    op.create_index(op.f('ix_usuarios_keycloak_id'), 'usuarios', ['keycloak_id'], unique=True)

    # Create dados_contrato table
    op.create_table(
        'dados_contrato',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('cpf_cliente', sa.String(length=11), nullable=False),
        sa.Column('numero_contrato', sa.String(length=50), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('endereco_assinatura', sa.Text(), nullable=True),
        sa.Column('arquivo_pdf_path', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dados_contrato_usuario_id', 'dados_contrato', ['usuario_id'], unique=False)
    op.create_index('idx_dados_contrato_cpf', 'dados_contrato', ['cpf_cliente'], unique=False)
    op.create_index('idx_dados_contrato_numero', 'dados_contrato', ['numero_contrato'], unique=False)
    op.create_index('idx_dados_contrato_status', 'dados_contrato', ['status'], unique=False)
    op.create_index('idx_dados_contrato_criado_em', 'dados_contrato', ['criado_em'], unique=False)
    op.create_index(op.f('ix_dados_contrato_cpf_cliente'), 'dados_contrato', ['cpf_cliente'], unique=False)
    op.create_index(op.f('ix_dados_contrato_id'), 'dados_contrato', ['id'], unique=False)
    op.create_index(op.f('ix_dados_contrato_numero_contrato'), 'dados_contrato', ['numero_contrato'], unique=False)
    op.create_index(op.f('ix_dados_contrato_status'), 'dados_contrato', ['status'], unique=False)

    # Create dados_bureau table
    op.create_table(
        'dados_bureau',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contrato_id', sa.Integer(), nullable=False),
        sa.Column('cpf_cliente', sa.String(length=11), nullable=False),
        sa.Column('nome_cliente', sa.String(length=255), nullable=False),
        sa.Column('logradouro', sa.Text(), nullable=False),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('cep', sa.String(length=8), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('data_consulta', sa.DateTime(), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['contrato_id'], ['dados_contrato.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dados_bureau_contrato_id', 'dados_bureau', ['contrato_id'], unique=False)
    op.create_index('idx_dados_bureau_cpf', 'dados_bureau', ['cpf_cliente'], unique=False)
    op.create_index('idx_dados_bureau_criado_em', 'dados_bureau', ['criado_em'], unique=False)
    op.create_index(op.f('ix_dados_bureau_cpf_cliente'), 'dados_bureau', ['cpf_cliente'], unique=False)
    op.create_index(op.f('ix_dados_bureau_id'), 'dados_bureau', ['id'], unique=False)

    # Create pareceres table
    op.create_table(
        'pareceres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contrato_id', sa.Integer(), nullable=False),
        sa.Column('distancia_km', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('tipo_parecer', sa.String(length=20), nullable=False),
        sa.Column('texto_parecer', sa.Text(), nullable=False),
        sa.Column('latitude_inicio', sa.Numeric(precision=10, scale=8), nullable=False),
        sa.Column('longitude_inicio', sa.Numeric(precision=11, scale=8), nullable=False),
        sa.Column('latitude_fim', sa.Numeric(precision=10, scale=8), nullable=False),
        sa.Column('longitude_fim', sa.Numeric(precision=11, scale=8), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['contrato_id'], ['dados_contrato.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contrato_id')
    )
    op.create_index('idx_parecer_contrato_id', 'pareceres', ['contrato_id'], unique=False)
    op.create_index('idx_parecer_tipo', 'pareceres', ['tipo_parecer'], unique=False)
    op.create_index('idx_parecer_criado_em', 'pareceres', ['criado_em'], unique=False)
    op.create_index(op.f('ix_pareceres_id'), 'pareceres', ['id'], unique=False)
    op.create_index(op.f('ix_pareceres_tipo_parecer'), 'pareceres', ['tipo_parecer'], unique=False)

    # Create logs_analise table
    op.create_table(
        'logs_analise',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contrato_id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('tipo_evento', sa.String(length=20), nullable=False),
        sa.Column('mensagem', sa.String(length=500), nullable=False),
        sa.Column('detalhes', sa.Text(), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['contrato_id'], ['dados_contrato.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_logs_analise_contrato_id', 'logs_analise', ['contrato_id'], unique=False)
    op.create_index('idx_logs_analise_usuario_id', 'logs_analise', ['usuario_id'], unique=False)
    op.create_index('idx_logs_analise_tipo_evento', 'logs_analise', ['tipo_evento'], unique=False)
    op.create_index('idx_logs_analise_criado_em', 'logs_analise', ['criado_em'], unique=False)
    op.create_index(op.f('ix_logs_analise_id'), 'logs_analise', ['id'], unique=False)


def downgrade() -> None:
    # Drop logs_analise table
    op.drop_index(op.f('ix_logs_analise_id'), table_name='logs_analise')
    op.drop_index('idx_logs_analise_criado_em', table_name='logs_analise')
    op.drop_index('idx_logs_analise_tipo_evento', table_name='logs_analise')
    op.drop_index('idx_logs_analise_usuario_id', table_name='logs_analise')
    op.drop_index('idx_logs_analise_contrato_id', table_name='logs_analise')
    op.drop_table('logs_analise')

    # Drop pareceres table
    op.drop_index(op.f('ix_pareceres_tipo_parecer'), table_name='pareceres')
    op.drop_index(op.f('ix_pareceres_id'), table_name='pareceres')
    op.drop_index('idx_parecer_criado_em', table_name='pareceres')
    op.drop_index('idx_parecer_tipo', table_name='pareceres')
    op.drop_index('idx_parecer_contrato_id', table_name='pareceres')
    op.drop_table('pareceres')

    # Drop dados_bureau table
    op.drop_index(op.f('ix_dados_bureau_id'), table_name='dados_bureau')
    op.drop_index(op.f('ix_dados_bureau_cpf_cliente'), table_name='dados_bureau')
    op.drop_index('idx_dados_bureau_criado_em', table_name='dados_bureau')
    op.drop_index('idx_dados_bureau_cpf', table_name='dados_bureau')
    op.drop_index('idx_dados_bureau_contrato_id', table_name='dados_bureau')
    op.drop_table('dados_bureau')

    # Drop dados_contrato table
    op.drop_index(op.f('ix_dados_contrato_status'), table_name='dados_contrato')
    op.drop_index(op.f('ix_dados_contrato_numero_contrato'), table_name='dados_contrato')
    op.drop_index(op.f('ix_dados_contrato_id'), table_name='dados_contrato')
    op.drop_index(op.f('ix_dados_contrato_cpf_cliente'), table_name='dados_contrato')
    op.drop_index('idx_dados_contrato_criado_em', table_name='dados_contrato')
    op.drop_index('idx_dados_contrato_status', table_name='dados_contrato')
    op.drop_index('idx_dados_contrato_numero', table_name='dados_contrato')
    op.drop_index('idx_dados_contrato_cpf', table_name='dados_contrato')
    op.drop_index('idx_dados_contrato_usuario_id', table_name='dados_contrato')
    op.drop_table('dados_contrato')

    # Drop usuarios table
    op.drop_index(op.f('ix_usuarios_keycloak_id'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_id'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_index('idx_usuario_ativo', table_name='usuarios')
    op.drop_index('idx_usuario_email', table_name='usuarios')
    op.drop_index('idx_usuario_keycloak_id', table_name='usuarios')
    op.drop_table('usuarios')

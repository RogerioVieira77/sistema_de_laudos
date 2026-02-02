-- ============================================
-- Init Script para PostgreSQL
-- Criar banco de dados e usuários adicionais
-- ============================================

-- Criar banco de dados para Keycloak
CREATE DATABASE keycloak
    ENCODING 'UTF8'
    LC_COLLATE 'pt_BR.UTF-8'
    LC_CTYPE 'pt_BR.UTF-8';

-- Conectar ao banco keycloak
\connect keycloak;

-- Criar extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Conectar de volta ao banco principal
\connect sistema_de_laudos;

-- Criar extensões no banco principal
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- ============================================
-- Criar schemas para organização
-- ============================================
CREATE SCHEMA IF NOT EXISTS laudos;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS cache;

-- ============================================
-- Criar função de auditoria
-- ============================================
CREATE TABLE IF NOT EXISTS audit.log (
    id SERIAL PRIMARY KEY,
    table_name TEXT,
    operation VARCHAR(10),
    user_name TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_data JSONB,
    new_data JSONB
);

CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit.log (table_name, operation, user_name, old_data, new_data)
    VALUES (TG_TABLE_NAME, TG_OP, CURRENT_USER, row_to_json(OLD), row_to_json(NEW));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Grant permissões ao usuário
-- ============================================
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO laudos_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA laudos GRANT ALL ON TABLES TO laudos_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT SELECT ON TABLES TO laudos_user;

GRANT USAGE ON SCHEMA public, laudos, audit TO laudos_user;
GRANT CREATE ON SCHEMA public TO laudos_user;

-- ============================================
-- Criar funções de utilidade
-- ============================================

-- Função para calcular distância entre dois pontos (Haversine)
CREATE OR REPLACE FUNCTION haversine_distance(
    lat1 FLOAT8,
    lon1 FLOAT8,
    lat2 FLOAT8,
    lon2 FLOAT8
)
RETURNS FLOAT8 AS $$
DECLARE
    R FLOAT8 := 6371; -- Raio da Terra em km
    delta_lat FLOAT8;
    delta_lon FLOAT8;
    a FLOAT8;
    c FLOAT8;
BEGIN
    delta_lat := RADIANS(lat2 - lat1);
    delta_lon := RADIANS(lon2 - lon1);
    a := SIN(delta_lat/2) * SIN(delta_lat/2) + 
         COS(RADIANS(lat1)) * COS(RADIANS(lat2)) * 
         SIN(delta_lon/2) * SIN(delta_lon/2);
    c := 2 * ASIN(SQRT(a));
    RETURN R * c;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- Criar índices de performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_laudos_created_at ON laudos.pareceres(criado_em DESC);
CREATE INDEX IF NOT EXISTS idx_laudos_contrato_id ON laudos.pareceres(contrato_id);

-- ============================================
-- Comentários e documentação
-- ============================================
COMMENT ON SCHEMA laudos IS 'Schema principal para dados de laudos de documentoscopia';
COMMENT ON SCHEMA audit IS 'Schema para logs de auditoria de mudanças';
COMMENT ON FUNCTION haversine_distance(FLOAT8, FLOAT8, FLOAT8, FLOAT8) IS 'Calcula distância em km entre dois pontos de latitude/longitude usando a fórmula de Haversine';

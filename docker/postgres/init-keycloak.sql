-- ============================================
-- Criar banco de dados e usuário para Keycloak
-- ============================================

-- Criar usuário para Keycloak (se não existir)
DO $$ BEGIN
    CREATE USER kcdbadmin_dev WITH PASSWORD 'Dev@)((42))';
EXCEPTION WHEN duplicate_object THEN
    -- Usuário já existe, apenas dar permissões
    ALTER USER kcdbadmin_dev WITH PASSWORD 'Dev@)((42))';
END $$;

-- Dar permissões ao usuário do Keycloak
ALTER USER kcdbadmin_dev CREATEDB;
ALTER USER kcdbadmin_dev SUPERUSER;

-- Dar permissões no banco keycloak_dev
GRANT ALL PRIVILEGES ON DATABASE keycloak_dev TO kcdbadmin_dev;

-- Conectar ao banco keycloak_dev e dar permissões
\connect keycloak_dev;

GRANT ALL ON SCHEMA public TO kcdbadmin_dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO kcdbadmin_dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO kcdbadmin_dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO kcdbadmin_dev;

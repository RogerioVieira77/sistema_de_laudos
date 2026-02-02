# FASE 2: INFRAESTRUTURA COM DOCKER
## Sistema de Laudos - Setup Completo

### 📋 Overview

Esta fase configura toda a infraestrutura de containerização do projeto usando Docker e Docker Compose. O setup inclui todos os 6 serviços principais + extras.

### 🐳 Serviços Configurados

| Serviço | Port | Descrição |
|---------|------|-----------|
| **PostgreSQL 16** | 5432 | Banco de dados principal |
| **Redis 7** | 6379 | Cache e fila para Celery |
| **Keycloak 23** | 8080 | Autenticação OAuth2 |
| **FastAPI** | 8000 | Backend API |
| **React + Vite** | 5173 | Frontend SPA |
| **Nginx** | 80/443 | Reverse Proxy |
| **Celery Worker** | - | Processamento assíncrono |
| **Flower** | 5555 | Monitor Celery |

---

## 🚀 Quick Start

### 1. Clone e Configure

```bash
# Ir para o diretório do projeto
cd /opt/app/sistema_de_laudos

# Copiar arquivo de exemplo de configuração
cp .env.example .env

# Editar .env com suas configurações (senhas, URLs, etc)
nano .env
```

### 2. Iniciar os Serviços

```bash
# Construir e iniciar todos os containers
docker compose up -d

# Verificar status
docker compose ps

# Ver logs de um serviço
docker compose logs -f backend
docker compose logs -f frontend
```

### 3. Esperar pela Inicialização

Os serviços levam alguns momentos para iniciar. Use health checks:

```bash
# Verificar health checks
docker compose exec postgres pg_isready -U laudos_user
docker compose exec redis redis-cli ping
docker compose exec backend curl http://localhost:8000/api/v1/health
```

### 4. Configurar Keycloak (Primeira Execução)

```bash
# Executar script de inicialização
bash docker/keycloak/init.sh

# Ou acessar manualmente em http://localhost:8080/admin
# Username: admin
# Password: (verificar .env KEYCLOAK_ADMIN_PASSWORD)
```

---

## 📁 Estrutura de Arquivos

```
sistema_de_laudos/
├── docker compose.yml          # Orquestração de containers
├── .env.example                # Variáveis de ambiente (exemplo)
├── .env                        # Variáveis de ambiente (seu arquivo)
├── .gitignore                  # Archivos a ignorar
│
├── backend/
│   ├── Dockerfile              # Construção da imagem FastAPI
│   ├── requirements.txt        # Dependências Python
│   └── app/                    # Código-fonte do backend
│       ├── main.py             # Inicialização FastAPI
│       ├── config.py           # Configurações
│       ├── api/
│       ├── services/
│       ├── models/
│       ├── repositories/
│       └── tasks/              # Tarefas Celery
│
├── frontend/
│   ├── Dockerfile              # Construção da imagem React
│   ├── package.json            # Dependências Node
│   ├── nginx.conf              # Config Nginx para SPA
│   └── src/                    # Código-fonte React
│       ├── main.jsx
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── hooks/
│
├── nginx/
│   ├── conf.d/
│   │   └── default.conf        # Config reverse proxy
│   └── ssl/                    # Certificados SSL
│
└── docker/
    ├── postgres/
    │   └── init.sql            # Script de inicialização DB
    └── keycloak/
        └── init.sh             # Script de setup Keycloak
```

---

## ⚙️ Configuração Detalhada

### PostgreSQL

**Variáveis de Ambiente:**
```
DB_HOST=postgres
DB_PORT=5432
DB_NAME=sistema_de_laudos
DB_USER=laudos_user
DB_PASSWORD=laudos_password_123
```

**Banco Criado:**
- `sistema_de_laudos` - Banco principal
- `keycloak` - Banco do Keycloak

**Inicialização:**
- Script `docker/postgres/init.sql` cria schemas, extensões e funções úteis
- Extensões: uuid-ossp, pg_trgm, btree_gin, btree_gist
- Função Haversine para cálculo de distância

### Redis

**Variáveis:**
```
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_123
```

**DBs:**
- DB 0: Cache geral (REDIS_URL)
- DB 1: Broker Celery (CELERY_BROKER_URL)
- DB 2: Result Backend (CELERY_RESULT_BACKEND)

### Keycloak

**Variáveis:**
```
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASSWORD=keycloak_admin_123
KEYCLOAK_PORT=8080
KEYCLOAK_REALM=sistema_laudos
```

**Clientes Criados pelo Script:**
1. `sistema_laudos_backend` - Backend API
2. `sistema_laudos_frontend` - Frontend React

**Roles Criados:**
- `admin`
- `analyst`
- `viewer`
- `supervisor`

**Usuário Demo:**
- Username: `demo`
- Password: `demo123456`

### FastAPI Backend

**Variáveis:**
```
BACKEND_PORT=8000
SECRET_KEY=your_secret_key_change_in_production
DATABASE_URL=postgresql://...
CELERY_BROKER_URL=redis://...
```

**Healthcheck:**
- Endpoint: `GET /api/v1/health`
- Intervalo: 15s

**Build Multi-stage:**
- Reduz tamanho da imagem (~400MB → ~300MB)
- Otimiza cache de dependências

### React Frontend

**Variáveis:**
```
FRONTEND_PORT=5173
VITE_API_URL=http://localhost:8000/api
VITE_KEYCLOAK_URL=http://localhost:8080
```

**Healthcheck:**
- Endpoint: `GET /`
- Intervalo: 15s

**Nginx SPA Routing:**
- Redireciona todas as rotas para `index.html`
- Suporta `react-router` corretamente
- Cache de assets estáticos

### Nginx Reverse Proxy

**Rotas Configuradas:**
```
/              → Frontend (React)
/api/          → Backend (FastAPI)
/docs          → Swagger UI
/redoc         → ReDoc
/auth/         → Keycloak
/realms/       → Keycloak
/resources/    → Keycloak assets
/js/           → Keycloak JS
```

**Headers de Segurança:**
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy

**Compressão:**
- GZIP ativado
- Tipos: JS, CSS, JSON, SVG

### Celery Worker

**Funcionalidades:**
- Processa tarefas assíncronas
- Conectado ao Redis como broker
- Configurado para 4 workers concorrentes
- Mesmas variáveis de ambiente que o backend

### Flower Monitor

**Acesso:**
- URL: `http://localhost:5555`
- Interface web para monitorar workers Celery
- Visualizar tarefas executadas

---

## 🔧 Comandos Úteis

### Gerenciamento dos Containers

```bash
# Iniciar
docker compose up -d

# Parar
docker compose down

# Parar e remover volumes (CUIDADO: deleta dados!)
docker compose down -v

# Rebuild de uma imagem
docker compose build --no-cache backend

# Ver logs
docker compose logs -f backend
docker compose logs -f frontend

# Executar comando em um container
docker compose exec backend bash
docker compose exec frontend sh
```

### Banco de Dados

```bash
# Conectar ao PostgreSQL
docker compose exec postgres psql -U laudos_user -d sistema_de_laudos

# Backup
docker compose exec postgres pg_dump -U laudos_user -d sistema_de_laudos > backup.sql

# Restore
cat backup.sql | docker compose exec -T postgres psql -U laudos_user -d sistema_de_laudos
```

### Redis

```bash
# CLI Redis
docker compose exec redis redis-cli -a redis_password_123

# Monitorar keys
docker compose exec redis redis-cli -a redis_password_123 KEYS "*"

# Limpar cache
docker compose exec redis redis-cli -a redis_password_123 FLUSHDB
```

### Keycloak

```bash
# Acessar Admin Console
# http://localhost:8080/admin/master/console

# Verificar status
docker compose exec keycloak curl http://localhost:8080/health/ready
```

---

## 📊 Volumes e Persistência

| Volume | Container | Tipo | Uso |
|--------|-----------|------|-----|
| `postgres_data` | PostgreSQL | Named | Dados do banco |
| `redis_data` | Redis | Named | Dados Redis |
| `nginx_logs` | Nginx | Named | Logs de acesso |
| `./backend` | Backend | Bind | Desenvolvimento |
| `./frontend` | Frontend | Bind | Desenvolvimento |

**Limpar Volumes:**
```bash
# Remover volumes nomeados (CUIDADO!)
docker volume rm sistema_de_laudos_postgres_data
docker volume rm sistema_de_laudos_redis_data

# Ver todos os volumes
docker volume ls | grep sistema_de_laudos
```

---

## 🌐 Acessos

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Frontend** | http://localhost | - |
| **Backend API** | http://localhost:8000 | - |
| **Swagger Docs** | http://localhost:8000/docs | - |
| **ReDoc** | http://localhost:8000/redoc | - |
| **Keycloak** | http://localhost:8080 | admin / keycloak_admin_123 |
| **Keycloak Realm** | http://localhost:8080/realms/sistema_laudos | - |
| **Flower** | http://localhost:5555 | - |

---

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker compose logs backend
docker compose logs frontend

# Verificar erros de build
docker compose build --no-cache backend
```

### Conexão recusada na porta

```bash
# Verificar se porta está em uso
lsof -i :8000
lsof -i :5173

# Mudar porta no .env
# BACKEND_PORT=8001
```

### PostgreSQL não inicializa

```bash
# Ver logs
docker compose logs postgres

# Remover volume e reiniciar
docker compose down -v
docker compose up postgres -d
```

### Redis não conecta

```bash
# Testar conexão
docker compose exec redis redis-cli -a redis_password_123 ping

# Verificar variáveis de ambiente
docker compose exec backend env | grep REDIS
```

### Keycloak não inicializa

```bash
# Aguardar mais tempo
sleep 30
docker compose logs keycloak

# Remover e reiniciar
docker compose down
docker compose up keycloak -d
```

---

## 🔐 Segurança

### Senhas Padrão (MUDE EM PRODUÇÃO!)

```
PostgreSQL: laudos_password_123
Redis: redis_password_123
Keycloak Admin: keycloak_admin_123
Demo User: demo123456
```

### Recomendações

1. **Mudar todas as senhas** antes de deploy
2. **Gerar SECRET_KEY** novo:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
3. **Usar SSL/TLS** em produção
4. **Configurar CORS** apropriadamente
5. **Não commitar .env** com dados reais
6. **Usar secrets manager** (AWS Secrets, Vault, etc)

---

## 📝 Próximos Passos

Após esta fase estar funcionando:

1. ✅ **FASE 2 CONCLUÍDA** - Infraestrutura Docker OK
2. **FASE 3** - Configurar Banco de Dados (Migrations Alembic)
3. **FASE 4** - Desenvolver Backend APIs
4. **FASE 5** - Desenvolver Frontend Components

---

## 📚 Referências

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Redis Docker](https://hub.docker.com/_/redis)
- [Keycloak Docker](https://hub.docker.com/r/keycloak/keycloak)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React + Vite](https://vitejs.dev/guide/)

---

## 💬 Suporte

Para problemas, verifique:
1. Logs dos containers
2. Arquivo `.env`
3. Portas em uso
4. Espaço em disco
5. Permissões de arquivo

---

**Status: ✅ FASE 2 CONFIGURADA**

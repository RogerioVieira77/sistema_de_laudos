# 🚀 Deploy - Sistema de Laudos

## Guia Completo de Implementação em Ambiente de Desenvolvimento

**Data:** 02/02/2026  
**Versão:** 2.0.0 (Atualizado com nova estrutura de pastas)  
**Ambiente:** Desenvolvimento (Dev)  
**Docker Compose:** v5.0.2 (Comandos sem hífen)

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Configuração Inicial](#configuração-inicial)
4. [Execução com Docker Compose](#execução-com-docker-compose)
5. [Verificação e Testes](#verificação-e-testes)
6. [Troubleshooting](#troubleshooting)
7. [Parar e Remover Containers](#parar-e-remover-containers)

---

## 🔧 Pré-requisitos

### Softwares Necessários

| Software | Versão Mínima | Instalação |
|----------|---------------|-----------|
| **Docker** | 24.0+ | [Instalar Docker](https://docs.docker.com/get-docker/) |
| **Docker Compose** | 2.20+ | Incluído no Docker Desktop |
| **Git** | 2.40+ | [Instalar Git](https://git-scm.com/) |
| **Linux/macOS/WSL2** | - | Obrigatório (não suporta Docker nativo no Windows 10/11) |

### Verificar Instalação

```bash
# Verificar Docker
docker --version
# Output: Docker version 24.0+

# Verificar Docker Compose
docker compose version
# Output: Docker Compose version 2.20+

# Verificar Git
git --version
# Output: git version 2.40+
```

### Requisitos de Sistema

- **CPU:** 2+ cores recomendado
- **RAM:** 4GB mínimo (8GB recomendado)
- **Disco:** 5GB livre
- **Rede:** Conexão com internet para download de imagens Docker

---

## 📁 Estrutura do Projeto

```
/opt/app/sistema_de_laudos/
├── docker-compose.yml              # Orquestração de containers (RAIZ)
├── .env.dev                        # Variáveis de ambiente (DEV)
├── Deploy.md                       # Este guia
├── ANALISE_INCONSISTENCIAS.md      # Análise de consistência
│
├── backend/
│   ├── Dockerfile                  # Build do backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # Aplicação FastAPI
│   │   ├── api/                    # Rotas/Endpoints
│   │   ├── models/                 # Modelos SQLAlchemy
│   │   ├── services/               # Lógica de negócio
│   │   └── tasks/                  # Tarefas Celery
│   ├── migrations/                 # Migrações Alembic
│   ├── requirements.txt            # Dependências Python
│   └── alembic.ini                 # Config. Alembic
│
├── frontend/
│   ├── Dockerfile                  # Build do frontend
│   ├── src/
│   │   ├── main.jsx                # Entrada da app React
│   │   ├── App.jsx                 # Componente principal
│   │   ├── index.css               # Estilos globais
│   │   └── components/             # Componentes React
│   ├── package.json                # Dependências Node.js
│   ├── package-lock.json
│   ├── vite.config.js              # Config. Vite
│   ├── nginx.conf                  # Config. Nginx (produção)
│   ├── index.html
│   └── node_modules/
│
├── nginx/
│   ├── nginx.conf                  # Config. principal Nginx
│   ├── conf.d/
│   │   └── default.conf            # Config. virtual hosts
│   └── ssl/                        # Certificados SSL
│
├── docker/
│   ├── postgres/
│   │   └── init.sql                # Script inicialização BD
│   └── keycloak/
│       └── init.sh                 # Script inicialização Keycloak
│
└── documentation/
    └── docs-gerais/                # Documentação adicional
```

**✅ Nova estrutura intuitiva e organizada:**
- `docker-compose.yml` está na **raiz do projeto**
- `.env.dev` está na **raiz do projeto**
- Cada serviço tem seu próprio **Dockerfile**
- Configurações do **nginx** em pasta separada
- Scripts de inicialização em pasta **docker/**

---

## ⚙️ Configuração Inicial

### Passo 1: Acessar a Pasta Raiz do Projeto

```bash
cd /opt/app/sistema_de_laudos

# Verificar se está no local correto
pwd
# Output: /opt/app/sistema_de_laudos

# Listar arquivos da raiz
ls -la
# Deve listar: docker-compose.yml, .env.dev, backend/, frontend/, nginx/, docker/, etc.
```

### Passo 2: Revisar Arquivo de Variáveis de Ambiente

O arquivo `.env.dev` já está configurado na raiz. Verifique os valores:

```bash
cat .env.dev
```

**Variáveis críticas a verificar:**

```env
# PostgreSQL
DB_NAME=sistema_de_laudos_dev       # ✅
DB_HOST=postgres                     # ✅ (nome do container)
DB_PORT=5432                         # ✅
DB_USER=dbadmin_dev                  # ✅
DB_PASSWORD=Dev@)((42))              # ✅

# Backend
BACKEND_PORT=8000                    # ✅
BACKEND_HOST=0.0.0.0                 # ✅
BACK_SECRET_KEY=Dev@)((42))          # ✅

# Frontend
FRONTEND_PORT=3000                   # ✅
VITE_API_URL=http://localhost:8000/api/v1  # ✅

# Redis
REDIS_PASSWORD=redisadmin_dev        # ✅
REDIS_PORT=6379                      # ✅

# Keycloak
KEYCLOAK_ADMIN_USER=kcadmin_dev      # ✅
KEYCLOAK_ADMIN_PASSWORD=Dev@)((42))  # ✅
KEYCLOAK_DB_NAME=keycloak_dev        # ✅
KEYCLOAK_DB_USER=kcdbadmin_dev       # ✅
KEYCLOAK_DB_PASSWORD=Dev@)((42))     # ✅

# Nginx
NGINX_HTTP_PORT=80                   # ✅
NGINX_HTTPS_PORT=443                 # ✅
```

### Passo 3: Validar docker-compose.yml

```bash
# Validar a sintaxe do arquivo
docker compose config

# Saída esperada: Arquivo completo sem erros
# Se houver erros, eles aparecerão nesta saída
```

### Passo 4: Criar Diretórios Necessários

```bash
# Criar diretórios se não existirem
mkdir -p nginx/ssl
mkdir -p nginx/conf.d
mkdir -p docker/postgres
mkdir -p docker/keycloak

# Verificar se Dockerfiles existem
ls -la backend/Dockerfile
ls -la frontend/Dockerfile
```

---

## 🐳 Execução com Docker Compose

### Passo 1: Build e Inicialização dos Containers

Na pasta raiz do projeto `/opt/app/sistema_de_laudos`, execute:

```bash
# Formato: docker compose (sem hífen) - Versão v5.0.2
docker compose --env-file .env.dev up -d
```

**O que este comando faz:**
- `--env-file .env.dev`: Carrega as variáveis de ambiente do arquivo na raiz
- `up`: Cria e inicia todos os containers definidos no docker-compose.yml
- `-d`: Executa em background (detached mode)

**Saída esperada:**
```
[+] Running 9/9
 ✔ Network sistema_de_laudos_sistema_laudos_net_dev       Created     0.1s
 ✔ Container sistema_de_laudos_postgres_dev               Created     0.2s
 ✔ Container sistema_laudos_redis_dev                     Created     0.2s
 ✔ Container sistema_laudos_backend_dev                   Created     0.2s
 ✔ Container sistema_laudos_frontend_dev                  Created     0.2s
 ✔ Container sistema_laudos_keycloak_dev                  Created     0.1s
 ✔ Container sistema_laudos_celery_dev                    Created     0.1s
 ✔ Container sistema_laudos_nginx_dev                     Created     0.4s
```

### Passo 2: Verificar Status dos Containers

```bash
# Listar todos os containers em execução
docker compose --env-file .env.dev ps

# Saída esperada:
# NAME                                   COMMAND                      STATUS
# sistema_de_laudos_postgres_dev         postgres                     Up (healthy)
# sistema_laudos_redis_dev               redis-server ...             Up (healthy)
# sistema_laudos_backend_dev             uvicorn app.main:app ...     Up (healthy)
# sistema_laudos_frontend_dev            npm run dev                  Up
# sistema_laudos_keycloak_dev            /opt/keycloak ...            Up (healthy)
# sistema_laudos_celery_dev              celery -A app.tasks ...      Up
# sistema_laudos_nginx_dev               nginx -g daemon off;         Up
```

### Passo 3: Monitorar Logs de Inicialização

```bash
# Ver logs em tempo real de TODOS os serviços
docker compose --env-file .env.dev logs -f

# Ou de um serviço específico
docker compose --env-file .env.dev logs -f backend

# Últimas 50 linhas do backend
docker compose --env-file .env.dev logs -f backend --tail=50
```

### Passo 4: Aguardar Inicialização Completa

Os serviços com `healthcheck` levam tempos diferentes para ficarem saudáveis:

| Serviço | Tempo | Status |
|---------|-------|--------|
| PostgreSQL | ~10s | Checking connectivity |
| Redis | ~10s | PONG response |
| Backend | ~15s | Health endpoint 200 |
| Frontend | ~20s | Build + npm dev server |
| Keycloak | ~30-60s | First startup longer |
| Celery | ~10s | Worker ready |
| Nginx | ~5s | Config validation |

**Monitorar em tempo real:**
```bash
# Executar em outro terminal
watch -n 2 'docker compose --env-file .env.dev ps'

# Pressione CTRL+C para sair
```

### Passo 5: Teste Rápido

Assim que os containers estiverem "Up":

```bash
# Backend Health Check
curl http://localhost:8000/api/v1/health

# Saída esperada:
# {"status":"healthy","service":"Sistema de Laudos Backend","version":"1.0.0"}

# Frontend
open http://localhost:3000
# ou acesse: http://localhost:3000 no navegador
```

---

## ✅ Verificação e Testes

### Passo 1: Verificar Conectividade dos Serviços

#### **PostgreSQL**

```bash
# Verificar se está acessível
docker compose exec postgres pg_isready -U dbadmin_dev

# Saída esperada: accepting connections

# Conectar ao banco de dados
docker compose exec postgres psql -U dbadmin_dev -d sistema_de_laudos_dev -c "SELECT version();"

# Saída esperada: PostgreSQL 16.x on ...
```

#### **Redis**

```bash
# Verificar conexão ao Redis
docker compose exec redis redis-cli -a redisadmin_dev ping

# Saída esperada: PONG
```

#### **Backend (FastAPI)**

```bash
# Testar endpoint de health check
curl http://localhost:8000/api/v1/health

# Saída esperada:
# {
#   "status": "healthy",
#   "service": "Sistema de Laudos Backend",
#   "version": "1.0.0"
# }

# Testar API raiz
curl http://localhost:8000/

# Saída esperada:
# {"message": "Sistema de Laudos API v1.0.0"}
```

#### **Frontend (React)**

```bash
# Acessar via browser
open http://localhost:3000
# ou
xdg-open http://localhost:3000
# ou copie e cole no navegador: http://localhost:3000
```

**Esperado:** Página do Sistema de Laudos carregada (React App Vite)

#### **Nginx**

```bash
# Verificar status do Nginx
docker compose exec nginx nginx -t

# Saída esperada:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

#### **Keycloak**

```bash
# Verificar health do Keycloak
curl http://localhost:8080/health/ready

# Saída esperada:
# {"status":"UP"}

# Acessar Admin Console
open http://localhost:8080/admin
# Credenciais:
# Username: kcadmin_dev
# Password: Dev@)((42))
```

### Passo 2: Testar Fluxo Completo da Aplicação

#### **1. Verificar Banco de Dados**

```bash
# Executar migrations (se necessário)
docker compose exec backend alembic upgrade head

# Verificar tabelas criadas
docker compose exec postgres psql -U dbadmin_dev -d sistema_de_laudos_dev -c "\dt"

# Saída esperada: Lista de tabelas criadas
```

#### **2. Testar Endpoints do Backend**

```bash
# Exemplo 1: GET /api/v1/health
curl -X GET http://localhost:8000/api/v1/health

# Exemplo 2: Com token JWT (se necessário)
curl -X GET http://localhost:8000/api/v1/laudos \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### **3. Fazer Login no Frontend**

```bash
# Acesse: http://localhost:3000
# Clique em "Login" ou similar
# Use credenciais do Keycloak ou dados de teste
```

### Passo 3: Verificar Persistência de Dados

```bash
# Verificar volumes criados
docker volume ls | grep sistema

# Saída esperada:
# sistema_de_laudos_postgres_data
# sistema_de_laudos_redis_data
# sistema_de_laudos_nginx_logs

# Inspecionar um volume específico
docker volume inspect sistema_de_laudos_postgres_data
```

---

## 🔍 Troubleshooting

### ⚠️ Erro: "uvicorn: executable file not found in $PATH"

**Causa:** Backend não conseguiu instalar as dependências Python no container

**Solução:**

```bash
# 1. Verificar logs do backend
docker compose logs backend

# 2. Limpar e reconstruir a imagem
docker compose down
docker compose build --no-cache backend

# 3. Iniciar novamente
docker compose up -d backend
```

---

### Problema: Container não inicia

**Solução:**

```bash
# Ver logs detalhados do serviço com erro
docker compose logs <nome_do_container>

# Exemplo:
docker compose logs backend

# Verificar se a porta já está em uso
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
```

---

### Problema: PostgreSQL não conecta

**Solução:**

```bash
# Verificar se o container está rodando
docker compose ps postgres

# Verificar logs
docker compose logs postgres

# Reiniciar o container
docker compose restart postgres

# Testar conexão
docker compose exec postgres pg_isready -U dbadmin_dev
```

---

### Problema: Frontend não aparece/carrega

**Verificar:**

```bash
# 1. Verificar se container está rodando
docker compose ps frontend

# 2. Verificar logs do frontend
docker compose logs frontend

# 3. Testar acesso à porta
curl http://localhost:3000

# 4. Reiniciar frontend
docker compose restart frontend
```

---

### Problema: Backend retorna erro 502

**Solução:**

```bash
# 1. Verificar se Backend está saudável
docker compose logs backend

# 2. Reiniciar Backend
docker compose restart backend

# 3. Verificar conectividade com BD
docker compose exec backend python -c \
  "import sqlalchemy; print('DB connection OK')"
```

---

### Problema: Redis/Celery não funciona

**Solução:**

```bash
# 1. Verificar Redis
docker compose exec redis redis-cli -a redisadmin_dev ping

# 2. Verificar logs do Celery
docker compose logs celery

# 3. Reiniciar ambos
docker compose restart redis celery
```

---

### Limpar e Reconstruir (Reset Completo)

```bash
# ⚠️ CUIDADO: Isso remove todos os containers, volumes e dados

# 1. Parar todos os containers
docker compose down

# 2. Remover volumes (PERDERÁ dados do BD)
docker volume rm \
  sistema_de_laudos_postgres_data \
  sistema_de_laudos_redis_data \
  sistema_de_laudos_nginx_logs

# 3. Reconstruir imagens sem cache
docker compose build --no-cache

# 4. Iniciar novamente
docker compose up -d

# 5. Executar migrations
docker compose exec backend alembic upgrade head
```

---

### Problema: Permissão negada em volumes

**Solução:**

```bash
# Verificar permissões
ls -la backend/
ls -la frontend/
ls -la nginx/

# Ajustar permissões se necessário
chmod 755 backend/Dockerfile
chmod 755 frontend/Dockerfile
chmod 755 nginx/nginx.conf
```

---

## 🛑 Parar e Remover Containers

### Parar os Containers (sem deletar)

```bash
# Parar todos os containers
docker compose stop

# Parar um container específico
docker compose stop backend
```

### Remover Containers (limpar tudo)

```bash
# Remover containers, mas preservar volumes e dados
docker compose down

# Remover containers E volumes (PERDERÁ dados)
docker compose down -v

# Remover tudo incluindo imagens built
docker compose down -v --rmi all
```

### Inspecionar Containers

```bash
# Ver informações detalhadas de um container
docker inspect sistema_laudos_backend_dev

# Ver estatísticas de resource (CPU, RAM)
docker stats sistema_laudos_backend_dev

# Ver processos rodando no container
docker top sistema_laudos_backend_dev

# Ver variáveis de ambiente
docker inspect sistema_laudos_backend_dev | grep -A 20 "Env"
```

### Ver Logs de um Serviço Parado

```bash
# Ver últimos logs do backend mesmo após parada
docker compose logs backend --tail=100
```

---

## 📊 Resumo de Portas e Endpoints

| Serviço | Porta | URL | Função |
|---------|-------|-----|--------|
| **Backend** | 8000 | http://localhost:8000 | API FastAPI |
| **Health Check** | 8000 | http://localhost:8000/api/v1/health | Status Backend |
| **Frontend** | 3000 | http://localhost:3000 | App React (Vite) |
| **PostgreSQL** | 5432 | localhost:5432 | Banco de Dados |
| **Redis** | 6379 | localhost:6379 | Cache/Fila |
| **Keycloak** | 8080 | http://localhost:8080 | Autenticação/Admin |
| **Keycloak Admin** | 8080 | http://localhost:8080/admin | Gerenciamento |
| **Nginx** | 80 | http://localhost | Reverse Proxy (HTTP) |
| **Nginx HTTPS** | 443 | https://localhost | Reverse Proxy (HTTPS) |

---

## 📋 Credenciais Padrão (Dev)

### PostgreSQL
- **User:** `dbadmin_dev`
- **Password:** `Dev@)((42))`
- **Database:** `sistema_de_laudos_dev`
- **Port:** `5432`

### Redis
- **Password:** `redisadmin_dev`
- **Port:** `6379`

### Keycloak Admin
- **Username:** `kcadmin_dev`
- **Password:** `Dev@)((42))`
- **URL:** http://localhost:8080/admin

### Backend
- **Secret Key:** `Dev@)((42))`
- **Algorithm:** `HS256`
- **Token Expiry:** `300` minutos

---

## 🔒 Segurança em Desenvolvimento

### ✅ Implementado

- Usuário não-root nos containers
- Variáveis sensíveis em `.env.dev`
- Health checks configurados
- Restart automático de containers
- Rede interna do Docker para comunicação
- Multi-stage builds otimizados
- Volumes separados para dados persistentes

### ⚠️ Para Melhorar (Produção)

- [ ] Usar senhas mais fortes e aleatórias
- [ ] Configurar SSL/HTTPS com certificados válidos
- [ ] Restringir CORS apenas para domínios permitidos
- [ ] Implementar rate limiting
- [ ] Adicionar logging centralizado (ELK Stack)
- [ ] Configurar backups automáticos do BD
- [ ] Implementar secrets management (Vault, etc)
- [ ] Monitoramento com Prometheus/Grafana

---

## 📈 Próximos Passos (Pós Deploy)

Após subir a aplicação com sucesso:

### 1. Configurar Keycloak ✅
```bash
# Acessar: http://localhost:8080/admin
# Credenciais: kcadmin_dev / Dev@)((42))

# Passos:
# - Criar realm: sistema_laudos_dev
# - Configurar clientes
# - Definir usuários e roles
# - Configurar OAuth2/OIDC
```

### 2. Executar Migrations 📦
```bash
docker compose exec backend alembic upgrade head
```

### 3. Popular Banco de Dados 🗄️
```bash
# - Importar dados iniciais
# - Configurar fixtures de teste
# - Seed inicial de usuários
```

### 4. Testar Funcionalidades 🧪
```bash
# - Upload de documentos PDF
# - Geração de laudos
# - Exportação em PDF
# - Geolocalização (Maps)
# - Integração Keycloak
```

### 5. Monitorar Performance 📊
```bash
# - Verificar logs regularmente
# - Monitorar uso de recursos (CPU, RAM, Disco)
# - Analisar latência de requisições
# - Ajustar configurações se necessário
```

### 6. Configurar Backups 💾
```bash
# - Backup automático do PostgreSQL
# - Backup de volumes críticos
# - Teste de restore
```

---

## 📞 Suporte e Documentação

- **Documentação FastAPI:** https://fastapi.tiangolo.com/
- **Documentação React:** https://react.dev/
- **Documentação Docker Compose:** https://docs.docker.com/compose/
- **Documentação PostgreSQL:** https://www.postgresql.org/docs/
- **Documentação Keycloak:** https://www.keycloak.org/documentation
- **Documentação Nginx:** https://nginx.org/en/docs/

---

## 🗂️ Referência Rápida de Comandos

### Build e Execução

```bash
# Compilar imagens
docker compose build

# Iniciar serviços
docker compose up -d

# Parar serviços
docker compose stop

# Remover tudo
docker compose down
```

### Logs e Debugging

```bash
# Logs em tempo real
docker compose logs -f

# Logs específico
docker compose logs backend

# Últimas 100 linhas
docker compose logs backend --tail=100
```

### Acesso aos Containers

```bash
# Bash interativo
docker compose exec backend bash

# Executar comando
docker compose exec backend python -c "print('test')"

# Psql PostgreSQL
docker compose exec postgres psql -U dbadmin_dev -d sistema_de_laudos_dev
```

### Inspeção

```bash
# Status dos serviços
docker compose ps

# Validar arquivo
docker compose config

# Volumes
docker volume ls

# Networks
docker network ls
```

---

## 📝 Notas Importantes

- ✅ **NUNCA** commit do arquivo `.env.dev` no Git
- ✅ Senhas padrão em desenvolvimento são simples para facilitar testes
- ✅ Para produção, criar arquivo `.env.prod` com senhas fortes
- ✅ Manter backups regulares do PostgreSQL
- ✅ Monitorar uso de espaço em disco regularmente
- ✅ Atualizar imagens Docker periodicamente
- ✅ Verificar compatibilidade com nova versão do Docker Compose
- ✅ Documentação adicional em `documentation/docs-gerais/`

---

## 📄 Histórico de Versões

| Versão | Data | Alterações |
|--------|------|-----------|
| 2.0.0 | 02/02/2026 | Estrutura simplificada (docker-compose.yml na raiz), comandos para Docker v5.0.2 sem hífen, correção de inconsistências |
| 1.0.0 | 02/02/2026 | Versão inicial com estrutura em `infra/docker-compose/` |

---

**Documento criado em:** 02/02/2026  
**Última atualização:** 02/02/2026  
**Status:** ✅ Completo e Atualizado  
**Docker Compose Version:** v5.0.2 (Comandos sem hífen)

Para dúvidas ou sugestões, consulte: `ANALISE_INCONSISTENCIAS.md`

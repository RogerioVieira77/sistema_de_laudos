# 🎯 QUICK REFERENCE - Backend & Frontend

Resumo executivo das configurações para containers Backend e Frontend.

---

## 📦 BACKEND - FastAPI

### Dados Essenciais

```yaml
Imagem:          python:3.12-slim
Porta:           8000
Container:       sistema_laudos_backend_dev
Build:           ./backend/Dockerfile
Health Check:    GET /api/v1/health

Dependências:
  - FastAPI 0.104.1
  - SQLAlchemy 2.0.23
  - redis 5.0.1
  - celery 5.3.4
  - geopy 2.3.0
  - haversine 2.7.0
  - PyMuPDF 1.23.8
  - pdfplumber 0.10.3

Conexões:
  - PostgreSQL: postgres:5432
  - Redis: redis:6379
  - Keycloak: keycloak:8080
```

### docker-compose.yml (Backend)

```yaml
backend:
  build:
    context: ./
    dockerfile: backend/Dockerfile
  container_name: sistema_laudos_backend_dev
  restart: unless-stopped
  
  environment:
    # App
    ENVIRONMENT: ${ENVIRONMENT}
    DEBUG: ${DEBUG}
    APP_NAME: ${APP_NAME}
    APP_VERSION: ${APP_VERSION}
    
    # Database
    DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
    
    # Redis
    REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    CELERY_BROKER_URL: redis://:${REDIS_PASSWORD}@redis:6379/1
    CELERY_RESULT_BACKEND: redis://:${REDIS_PASSWORD}@redis:6379/2
    
    # Security
    SECRET_KEY: ${SECRET_KEY}
    ALGORITHM: ${ALGORITHM}
    ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES}
    
    # Keycloak
    KEYCLOAK_HOSTNAME: ${KEYCLOAK_HOSTNAME}
    KEYCLOAK_REALM: ${KEYCLOAK_REALM}
    KEYCLOAK_CLIENT_ID: ${KEYCLOAK_CLIENT_ID}
    KEYCLOAK_CLIENT_SECRET: ${KEYCLOAK_CLIENT_SECRET}
    
    # External APIs
    NOMINATIM_ENDPOINT: ${NOMINATIM_ENDPOINT}
    NOMINATIM_RATE_LIMIT: ${NOMINATIM_RATE_LIMIT}
  
  ports:
    - "${BACKEND_PORT}:8000"
  
  volumes:
    - ./backend:/app
    - /app/__pycache__
  
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
  
  networks:
    - sistema_laudos_net_dev
  
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### .env.dev (Backend)

```bash
# Backend
BACKEND_PORT=8000
SECRET_KEY=Dev@)((42))
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=300

# Database
DATABASE_URL=postgresql://dbadmin_dev:Dev@)((42))@postgres:5432/sistema_de_laudos_dev

# Redis
REDIS_URL=redis://:redisadmin_dev@redis:6379/0
CELERY_BROKER_URL=redis://:redisadmin_dev@redis:6379/1
CELERY_RESULT_BACKEND=redis://:redisadmin_dev@redis:6379/2

# Keycloak
KEYCLOAK_HOSTNAME=localhost:8080
KEYCLOAK_REALM=sistema_laudos_dev
KEYCLOAK_CLIENT_ID=sistema_laudos_backend_dev
KEYCLOAK_CLIENT_SECRET=Dev@)((42))

# External
NOMINATIM_ENDPOINT=https://nominatim.openstreetmap.org
NOMINATIM_RATE_LIMIT=1
```

### Dockerfile (Backend)

```dockerfile
# Builder
FROM python:3.12-slim as builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user --no-warn-script-location --compile -r requirements.txt

# Runtime
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client curl
RUN useradd -m -u 1000 appuser
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser backend/app /app/app

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Rotas Implementadas (Backend)

```
GET  /api/v1/health                        - Health check
GET  /api/v1/contratos                     - Listar contratos
POST /api/v1/contratos/upload              - Upload PDF contrato
GET  /api/v1/contratos/{id}                - Detalhes contrato
GET  /api/v1/geolocalizacao/{id}           - Análise geolocalização
GET  /api/v1/bureau/{cnpj}                 - Buscar no bureau
POST /api/v1/pareceres                     - Gerar parecer
GET  /api/v1/pareceres/{id}                - Detalhes parecer
```

---

## 🎨 FRONTEND - React + Vite

### Dados Essenciais

```yaml
Builder:         node:20-alpine
Runtime:         nginx:alpine
Porta:           80 (Nginx) / 5173 (Dev)
Container:       sistema_laudos_frontend_dev
Build:           ./frontend/Dockerfile
Health Check:    GET /

Dependências:
  - react 18.2.0
  - react-router-dom 6.20.0
  - axios 1.6.2
  - leaflet 1.9.4
  - react-leaflet 4.2.1
  - keycloak-js 23.0.0
  - zustand 4.4.7

Conexões:
  - Backend API: backend:8000
  - Keycloak: keycloak:8080
```

### docker-compose.yml (Frontend)

```yaml
frontend:
  build:
    context: ./
    dockerfile: frontend/Dockerfile
  container_name: sistema_laudos_frontend_dev
  restart: unless-stopped
  
  environment:
    # API
    VITE_API_URL: ${VITE_API_URL}
    
    # Keycloak
    VITE_KEYCLOAK_URL: ${VITE_KEYCLOAK_URL}
    VITE_KEYCLOAK_REALM: ${VITE_KEYCLOAK_REALM}
    VITE_KEYCLOAK_CLIENT_ID: ${VITE_KEYCLOAK_CLIENT_ID}
    
    # Debug
    VITE_DEBUG: ${VITE_DEBUG}
  
  ports:
    - "${FRONTEND_PORT}:80"
  
  volumes:
    - ./frontend/src:/usr/share/nginx/html/src
  
  depends_on:
    - backend
  
  networks:
    - sistema_laudos_net_dev
  
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost/"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### .env.dev (Frontend)

```bash
# Frontend
FRONTEND_PORT=5173

# API
VITE_API_URL=http://localhost:8000/api

# Keycloak
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=sistema_laudos_dev
VITE_KEYCLOAK_CLIENT_ID=sistema_laudos_frontend

# Debug
VITE_DEBUG=true
```

### Dockerfile (Frontend)

```dockerfile
# Builder
FROM node:20-alpine as builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/index.html .
COPY frontend/vite.config.js .
RUN npm run build

# Runtime
FROM nginx:alpine
RUN apk add --no-cache curl
RUN if ! id -u nginx > /dev/null 2>&1; then addgroup -g 101 nginx && adduser -D -u 101 -H -G nginx nginx; fi
COPY frontend/nginx.conf /etc/nginx/nginx.conf
COPY frontend/default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost || exit 1

USER nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Páginas (Frontend)

```
/                                    - Dashboard
/upload                              - Upload PDF
/results/:id                         - Resultados
```

---

## 🔐 Variáveis de Ambiente Consolidadas

```bash
# ============================================
# BACKEND & FRONTEND COMBINADOS
# ============================================

# Geral
ENVIRONMENT=development
DEBUG=true
APP_NAME="Sistema de Laudos - Dev"
APP_VERSION=1.0.0

# PostgreSQL
DB_NAME=sistema_de_laudos_dev
DB_HOST=postgres
DB_PORT=5432
DB_USER=dbadmin_dev
DB_PASSWORD=Dev@)((42))
DATABASE_URL=postgresql://dbadmin_dev:Dev@)((42))@postgres:5432/sistema_de_laudos_dev

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redisadmin_dev
REDIS_URL=redis://:redisadmin_dev@redis:6379/0

# Keycloak
KEYCLOAK_HOSTNAME=localhost:8080
KEYCLOAK_REALM=sistema_laudos_dev
KEYCLOAK_CLIENT_ID=sistema_laudos_backend_dev
KEYCLOAK_CLIENT_SECRET=Dev@)((42))
KEYCLOAK_ADMIN_USER=kcadmin_dev
KEYCLOAK_ADMIN_PASSWORD=Dev@)((42))
KEYCLOAK_PORT=8080
KEYCLOAK_DB_NAME=keycloak_dev
KEYCLOAK_DB_USER=kcdbadmin_dev
KEYCLOAK_DB_PASSWORD=Dev@)((42))

# Backend
BACKEND_PORT=8000
SECRET_KEY=Dev@)((42))
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=300
CELERY_BROKER_URL=redis://:redisadmin_dev@redis:6379/1
CELERY_RESULT_BACKEND=redis://:redisadmin_dev@redis:6379/2

# Frontend
FRONTEND_PORT=5173
VITE_API_URL=http://localhost:8000/api
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=sistema_laudos_dev
VITE_KEYCLOAK_CLIENT_ID=sistema_laudos_frontend
VITE_DEBUG=true

# External APIs
NOMINATIM_ENDPOINT=https://nominatim.openstreetmap.org
NOMINATIM_RATE_LIMIT=1

# Nginx
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# Flower
FLOWER_PORT=5555
```

---

## 🚀 Comandos de Build e Deploy

### Build

```bash
# Ambos
docker compose --env-file .env.dev build backend frontend

# Apenas Backend
docker compose --env-file .env.dev build backend

# Apenas Frontend
docker compose --env-file .env.dev build frontend

# Sem cache
docker compose --env-file .env.dev build --no-cache
```

### Start

```bash
# Ambos
docker compose --env-file .env.dev up -d backend frontend

# Com logs
docker compose --env-file .env.dev up backend frontend

# Todos os serviços
docker compose --env-file .env.dev up -d
```

### Status & Logs

```bash
# Status
docker compose --env-file .env.dev ps

# Logs Backend
docker compose --env-file .env.dev logs -f backend

# Logs Frontend
docker compose --env-file .env.dev logs -f frontend

# Todos os logs
docker compose --env-file .env.dev logs -f
```

### Stop

```bash
# Parar
docker compose --env-file .env.dev down

# Parar e remover volumes
docker compose --env-file .env.dev down -v
```

---

## 📊 Portas e URLs

| Serviço | Porta | URL |
|---------|-------|-----|
| Frontend | 80 | http://localhost |
| Backend | 8000 | http://localhost:8000 |
| Backend Docs | 8000 | http://localhost:8000/api/docs |
| Backend Health | 8000 | http://localhost:8000/api/v1/health |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| Keycloak | 8080 | http://localhost:8080 |
| Flower | 5555 | http://localhost:5555 |

---

## ✅ Checklist

- [ ] .env.dev criado e configurado
- [ ] backend/requirements.txt atualizado
- [ ] backend/Dockerfile buildável
- [ ] frontend/package.json configurado
- [ ] frontend/Dockerfile buildável
- [ ] docker-compose.yml com Backend e Frontend
- [ ] Backend inicia sem erros
- [ ] Frontend inicia sem erros
- [ ] Backend acessível em :8000
- [ ] Frontend acessível em :80/:5173
- [ ] Health checks passando

---

**Última atualização**: 02/02/2026  
**Status**: ✅ Pronto para uso

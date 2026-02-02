# 🐳 BACKEND E FRONTEND - Configuração Docker Compose

Documento com as configurações necessárias para criar os containers de Backend e Frontend.

---

## 📋 ÍNDICE
1. [Backend (FastAPI)](#backend-fastapi)
2. [Frontend (React + Vite)](#frontend-react--vite)
3. [Variáveis de Ambiente](#variáveis-de-ambiente)
4. [docker-compose.yml](#docker-composeyml)
5. [.env.dev Completo](#envdev-completo)
6. [Comandos de Execução](#comandos-de-execução)

---

## 🔧 BACKEND (FastAPI)

### Especificações Técnicas

| Item | Valor |
|------|-------|
| **Imagem Base** | `python:3.12-slim` |
| **Porta** | `8000` |
| **Serviço** | `backend` |
| **Container Name** | `sistema_laudos_backend_dev` |
| **Runtime** | `uvicorn` |
| **Framework** | `FastAPI 0.104.1+` |

### Dockerfile - Backend

```dockerfile
# Multi-stage build - Builder Stage
FROM python:3.12-slim as builder

WORKDIR /build

# Instalar dependências do build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY backend/requirements.txt .

# Compilar wheels
RUN pip install --no-cache-dir --user --no-warn-script-location \
    --compile -r requirements.txt

# ============================================
# Multi-stage build - Runtime Stage
# ============================================
FROM python:3.12-slim

WORKDIR /app

# Instalar dependências de runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd -m -u 1000 appuser

# Copiar dependências do builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copiar código da aplicação
COPY --chown=appuser:appuser backend/app /app/app

# Variáveis de PATH
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Trocar para usuário não-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### requirements.txt - Backend

```
# Web Framework
FastAPI==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
PyJWT>=2.6.0

# Database
SQLAlchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0

# Cache/Queue
redis==5.0.1
celery==5.3.4

# Geolocation & PDF
geopy==2.3.0
haversine==2.7.0
PyPDF2==3.0.1
PyMuPDF==1.23.8
pdfplumber==0.10.3

# HTTP Client
requests==2.31.0
aiohttp==3.9.1

# Validation & Serialization
python-dateutil==2.8.2
pytz==2023.3

# Logging & Monitoring
python-json-logger==2.0.7
prometheus-client==0.19.0

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
isort==5.13.2
mypy==1.7.0

# CORS
fastapi-cors==0.0.6
```

### Estrutura de Diretórios - Backend

```
backend/
├── Dockerfile
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── security.py             # JWT + Auth
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── contratos.py        # POST /contratos/upload
│   │   ├── geolocalizacao.py   # GET /geolocalizacao/{id}
│   │   ├── bureau.py           # GET /bureau/{cnpj}
│   │   ├── pareceres.py        # POST /pareceres
│   │   └── health.py           # GET /health
│   ├── models/
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── contrato.py
│   │   ├── parecer.py
│   │   └── audit.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── contrato.py
│   │   ├── parecer.py
│   │   └── user.py
│   ├── tasks/                  # Celery tasks
│   │   ├── __init__.py
│   │   ├── pdf_extraction.py
│   │   ├── geolocation.py
│   │   └── bureau_lookup.py
│   └── utils/
│       ├── __init__.py
│       ├── pdf_handler.py
│       ├── geo_handler.py
│       └── validators.py
├── alembic/
│   ├── versions/               # Migration files
│   ├── env.py
│   └── script.py.mako
└── tests/
    ├── __init__.py
    ├── test_api.py
    └── test_tasks.py
```

### Variáveis de Ambiente - Backend

```bash
# Aplicação
BACKEND_PORT=8000
SECRET_KEY=Dev@)((42))
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=300
DEBUG=true
ENVIRONMENT=development

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=sistema_de_laudos_dev
DB_USER=dbadmin_dev
DB_PASSWORD=Dev@)((42))
DATABASE_URL=postgresql://dbadmin_dev:Dev@)((42))@postgres:5432/sistema_de_laudos_dev

# Redis/Cache
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redisadmin_dev
REDIS_URL=redis://:redisadmin_dev@redis:6379/0

# Celery
CELERY_BROKER_URL=redis://:redisadmin_dev@redis:6379/1
CELERY_RESULT_BACKEND=redis://:redisadmin_dev@redis:6379/2

# Keycloak
KEYCLOAK_HOSTNAME=localhost:8080
KEYCLOAK_REALM=sistema_laudos_dev
KEYCLOAK_CLIENT_ID=sistema_laudos_backend_dev
KEYCLOAK_CLIENT_SECRET=Dev@)((42))

# External APIs
NOMINATIM_ENDPOINT=https://nominatim.openstreetmap.org
NOMINATIM_RATE_LIMIT=1

# Bureau Database (Optional)
# BUREAU_DB_HOST=bureau.example.com
# BUREAU_DB_PORT=3306
# BUREAU_DB_USER=bureau_user
# BUREAU_DB_PASSWORD=bureau_password
# BUREAU_DB_NAME=bureau_database
```

### Exemplo main.py - Backend

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from app.config import settings
from app.routes import contratos, geolocalizacao, pareceres, bureau, health

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="Sistema de Laudos API",
    description="API para análise de contratos com geolocalização",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
)

# Routes
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(contratos.router, prefix="/api/v1/contratos", tags=["contratos"])
app.include_router(geolocalizacao.router, prefix="/api/v1/geolocalizacao", tags=["geolocalizacao"])
app.include_router(bureau.router, prefix="/api/v1/bureau", tags=["bureau"])
app.include_router(pareceres.router, prefix="/api/v1/pareceres", tags=["pareceres"])

@app.on_event("startup")
async def startup_event():
    logger.info("Backend iniciado")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Backend finalizado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

---

## 🎨 FRONTEND (React + Vite)

### Especificações Técnicas

| Item | Valor |
|------|-------|
| **Imagem Base** | `node:20-alpine` (builder) → `nginx:alpine` (runtime) |
| **Porta** | `5173` (dev) / `80` (production) |
| **Serviço** | `frontend` |
| **Container Name** | `sistema_laudos_frontend_dev` |
| **Runtime** | `Nginx` |
| **Framework** | `React 18.2.0 + Vite 5.0.8` |

### Dockerfile - Frontend

```dockerfile
# Multi-stage build - Builder Stage
FROM node:20-alpine as builder

WORKDIR /app

# Copiar package.json e package-lock.json
COPY frontend/package*.json ./

# Instalar dependências
RUN npm ci

# Copiar código fonte
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/index.html .
COPY frontend/vite.config.js .
COPY frontend/postcss.config.js .
COPY frontend/tailwind.config.js .

# Build
RUN npm run build

# ============================================
# Runtime Stage - Nginx
# ============================================
FROM nginx:alpine

WORKDIR /app

# Instalar curl para healthcheck
RUN apk add --no-cache curl

# Criar usuário nginx (se não existir)
RUN if ! id -u nginx > /dev/null 2>&1; then \
    addgroup -g 101 nginx && \
    adduser -D -u 101 -H -G nginx nginx; \
    fi

# Copiar config Nginx
COPY frontend/nginx.conf /etc/nginx/nginx.conf
COPY frontend/default.conf /etc/nginx/conf.d/default.conf

# Copiar build do builder
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost || exit 1

# Usuário não-root
USER nginx

# Comando de inicialização
CMD ["nginx", "-g", "daemon off;"]
```

### package.json - Frontend

```json
{
  "name": "sistema-de-laudos-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0 --port 5173",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .js,.jsx",
    "format": "prettier --write \"src/**/*.{js,jsx,css}\"",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "leaflet": "^1.9.4",
    "react-leaflet": "^4.2.1",
    "keycloak-js": "^23.0.0",
    "zustand": "^4.4.7",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.6",
    "postcss": "^8.4.32",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.55.0",
    "eslint-plugin-react": "^7.33.2",
    "prettier": "^3.1.0",
    "typescript": "^5.3.3"
  }
}
```

### Estrutura de Diretórios - Frontend

```
frontend/
├── Dockerfile
├── package.json
├── package-lock.json
├── vite.config.js
├── index.html
├── public/
│   └── favicon.svg
├── src/
│   ├── main.jsx                # React entry point
│   ├── App.jsx                 # Main app component
│   ├── App.css
│   ├── index.css
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── MapView.jsx         # Leaflet map component
│   │   ├── UploadForm.jsx      # PDF upload form
│   │   ├── ResultsDisplay.jsx  # Results display
│   │   └── Footer.jsx
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── Upload.jsx
│   │   ├── Results.jsx
│   │   └── NotFound.jsx
│   ├── services/
│   │   ├── api.js             # Axios instance
│   │   ├── keycloak.js        # Keycloak config
│   │   └── storage.js         # LocalStorage utils
│   ├── store/
│   │   └── appStore.js        # Zustand store
│   ├── hooks/
│   │   ├── useAuth.js
│   │   └── useApi.js
│   └── utils/
│       ├── constants.js
│       └── formatters.js
├── nginx.conf                  # Nginx config
└── default.conf               # Nginx vhost config
```

### Variáveis de Ambiente - Frontend

```bash
# Aplicação
FRONTEND_PORT=5173
VITE_APP_NAME="Sistema de Laudos"
VITE_APP_VERSION="1.0.0"

# API Backend
VITE_API_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000

# Keycloak
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=sistema_laudos_dev
VITE_KEYCLOAK_CLIENT_ID=sistema_laudos_frontend

# Maps (Leaflet + Nominatim)
VITE_MAP_CENTER=["-15.7939", "-47.8822"]
VITE_MAP_ZOOM=10

# Debug
VITE_DEBUG=true
```

### Exemplo main.jsx - Frontend

```jsx
// src/main.jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'
import './App.css'
import { initKeycloak } from './services/keycloak'

// Inicializar Keycloak
initKeycloak().then(() => {
  ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </React.StrictMode>,
  )
})
```

### Exemplo App.jsx - Frontend

```jsx
// src/App.jsx
import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Results from './pages/Results'
import NotFound from './pages/NotFound'
import { useAuthStore } from './store/appStore'

function App() {
  const { user, setUser } = useAuthStore()

  useEffect(() => {
    // Check authentication status
    console.log('App initialized')
  }, [])

  return (
    <div className="app">
      <Header />
      <main className="container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/results/:id" element={<Results />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

export default App
```

### nginx.conf - Frontend

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml application/atom+xml image/svg+xml;

    include /etc/nginx/conf.d/*.conf;
}
```

### default.conf - Frontend (Nginx vhost)

```nginx
server {
    listen 80 default_server;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline' 'unsafe-eval'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; connect-src 'self' http: https:;" always;

    # Cache busting for assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA routing - todas as rotas vão para index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (opcional, se não usar reverse proxy central)
    # location /api/ {
    #     proxy_pass http://backend:8000/api/;
    #     proxy_http_version 1.1;
    #     proxy_set_header Upgrade $http_upgrade;
    #     proxy_set_header Connection 'upgrade';
    #     proxy_set_header Host $host;
    #     proxy_cache_bypass $http_upgrade;
    # }
}
```

---

## 🔐 Variáveis de Ambiente

### .env.dev Completo

```bash
# ============================================
# Configurações Gerais
# ============================================
ENVIRONMENT=development
DEBUG=true
APP_NAME="Sistema de Laudos - Dev"
APP_VERSION=1.0.0

# ============================================
# PostgreSQL
# ============================================
DB_NAME=sistema_de_laudos_dev
DB_HOST=postgres
DB_PORT=5432
DB_USER=dbadmin_dev
DB_PASSWORD=Dev@)((42))
DATABASE_URL=postgresql://dbadmin_dev:Dev@)((42))@postgres:5432/sistema_de_laudos_dev

# ============================================
# Redis
# ============================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redisadmin_dev
REDIS_URL=redis://:redisadmin_dev@redis:6379/0

# ============================================
# Keycloak
# ============================================
KEYCLOAK_HOSTNAME=localhost:8080
KEYCLOAK_REALM=sistema_laudos_dev
KEYCLOAK_CLIENT_ID=sistema_laudos_backend_dev
KEYCLOAK_CLIENT_SECRET=Dev@)((42))
KEYCLOAK_ADMIN_USER=kcadmin_dev
KEYCLOAK_ADMIN_PASSWORD=Dev@)((42))
KEYCLOAK_PORT=8080

# Keycloak Database
KEYCLOAK_DB_NAME=keycloak_dev
KEYCLOAK_DB_USER=kcdbadmin_dev
KEYCLOAK_DB_PASSWORD=Dev@)((42))

# ============================================
# Backend (FastAPI)
# ============================================
BACKEND_PORT=8000
SECRET_KEY=Dev@)((42))
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=300

# Celery Broker & Result Backend
CELERY_BROKER_URL=redis://:redisadmin_dev@redis:6379/1
CELERY_RESULT_BACKEND=redis://:redisadmin_dev@redis:6379/2

# ============================================
# Frontend (React + Vite)
# ============================================
FRONTEND_PORT=5173
VITE_API_URL=http://localhost:8000/api
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=sistema_laudos_dev
VITE_KEYCLOAK_CLIENT_ID=sistema_laudos_frontend
VITE_DEBUG=true

# ============================================
# Nginx
# ============================================
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# ============================================
# Flower (Celery Monitoring)
# ============================================
FLOWER_PORT=5555

# ============================================
# External APIs
# ============================================
NOMINATIM_ENDPOINT=https://nominatim.openstreetmap.org
NOMINATIM_RATE_LIMIT=1

# ============================================
# Bureau Database (Optional/External)
# ============================================
# BUREAU_DB_HOST=bureau.example.com
# BUREAU_DB_PORT=3306
# BUREAU_DB_USER=bureau_user
# BUREAU_DB_PASSWORD=bureau_password
# BUREAU_DB_NAME=bureau_database
```

---

## 🐳 docker-compose.yml - Backend e Frontend

### Serviço Backend

```yaml
  # ============================================
  # Aplicação Backend (FastAPI)
  # ============================================
  backend:
    build:
      context: ./
      dockerfile: backend/Dockerfile
    container_name: sistema_laudos_backend_dev
    restart: unless-stopped
    
    environment:
      # Geral
      ENVIRONMENT: ${ENVIRONMENT:?ENVIRONMENT is required}
      DEBUG: ${DEBUG:?DEBUG is required}
      APP_NAME: ${APP_NAME:?APP_NAME is required}
      APP_VERSION: ${APP_VERSION:?APP_VERSION is required}
      
      # Database
      DATABASE_URL: postgresql://${DB_USER:?DB_USER is required}:${DB_PASSWORD:?DB_PASSWORD is required}@postgres:5432/${DB_NAME:?DB_NAME is required}
      
      # Redis
      REDIS_URL: redis://:${REDIS_PASSWORD:?REDIS_PASSWORD is required}@redis:6379/0
      
      # Celery
      CELERY_BROKER_URL: redis://:${REDIS_PASSWORD:?REDIS_PASSWORD is required}@redis:6379/1
      CELERY_RESULT_BACKEND: redis://:${REDIS_PASSWORD:?REDIS_PASSWORD is required}@redis:6379/2
      
      # Security
      SECRET_KEY: ${SECRET_KEY:?SECRET_KEY is required}
      ALGORITHM: ${ALGORITHM:?ALGORITHM is required}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES:?ACCESS_TOKEN_EXPIRE_MINUTES is required}
      
      # Keycloak
      KEYCLOAK_HOSTNAME: ${KEYCLOAK_HOSTNAME:?KEYCLOAK_HOSTNAME is required}
      KEYCLOAK_REALM: ${KEYCLOAK_REALM:?KEYCLOAK_REALM is required}
      KEYCLOAK_CLIENT_ID: ${KEYCLOAK_CLIENT_ID:?KEYCLOAK_CLIENT_ID is required}
      KEYCLOAK_CLIENT_SECRET: ${KEYCLOAK_CLIENT_SECRET:?KEYCLOAK_CLIENT_SECRET is required}
      
      # External APIs
      NOMINATIM_ENDPOINT: ${NOMINATIM_ENDPOINT:?NOMINATIM_ENDPOINT is required}
      NOMINATIM_RATE_LIMIT: ${NOMINATIM_RATE_LIMIT:?NOMINATIM_RATE_LIMIT is required}
    
    ports:
      - "${BACKEND_PORT:?BACKEND_PORT is required}:8000"
    
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
      start_period: 40s
```

### Serviço Frontend

```yaml
  # ============================================
  # Aplicação Frontend (React + Vite)
  # ============================================
  frontend:
    build:
      context: ./
      dockerfile: frontend/Dockerfile
    container_name: sistema_laudos_frontend_dev
    restart: unless-stopped
    
    environment:
      # API Backend
      VITE_API_URL: ${VITE_API_URL:?VITE_API_URL is required}
      
      # Keycloak
      VITE_KEYCLOAK_URL: ${VITE_KEYCLOAK_URL:?VITE_KEYCLOAK_URL is required}
      VITE_KEYCLOAK_REALM: ${VITE_KEYCLOAK_REALM:?VITE_KEYCLOAK_REALM is required}
      VITE_KEYCLOAK_CLIENT_ID: ${VITE_KEYCLOAK_CLIENT_ID:?VITE_KEYCLOAK_CLIENT_ID is required}
      
      # Debug
      VITE_DEBUG: ${VITE_DEBUG:?VITE_DEBUG is required}
    
    ports:
      - "${FRONTEND_PORT:?FRONTEND_PORT is required}:80"
    
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
      start_period: 40s
```

---

## 🚀 Comandos de Execução

### Build dos Containers

```bash
# Build apenas Backend
docker compose --env-file .env.dev build backend

# Build apenas Frontend
docker compose --env-file .env.dev build frontend

# Build Backend e Frontend
docker compose --env-file .env.dev build backend frontend

# Build sem cache
docker compose --env-file .env.dev build --no-cache backend frontend
```

### Iniciar Containers

```bash
# Iniciar Backend e Frontend (com dependências)
docker compose --env-file .env.dev up -d backend frontend

# Iniciar todos os serviços
docker compose --env-file .env.dev up -d

# Iniciar e ver logs em tempo real
docker compose --env-file .env.dev up backend frontend
```

### Verificar Status

```bash
# Listar containers
docker compose --env-file .env.dev ps

# Ver logs do Backend
docker compose --env-file .env.dev logs -f backend

# Ver logs do Frontend
docker compose --env-file .env.dev logs -f frontend

# Ver logs de ambos
docker compose --env-file .env.dev logs -f backend frontend
```

### Acessar Containers

```bash
# Shell do Backend
docker compose --env-file .env.dev exec backend bash

# Shell do Frontend
docker compose --env-file .env.dev exec frontend sh

# Python shell no Backend
docker compose --env-file .env.dev exec backend python -c "import app"
```

### Parar e Remover

```bash
# Parar containers
docker compose --env-file .env.dev down

# Remover containers e volumes
docker compose --env-file .env.dev down -v

# Remover containers, volumes e imagens
docker compose --env-file .env.dev down -v --rmi all
```

---

## 📊 Portas Utilizadas

| Serviço | Porta | URL |
|---------|-------|-----|
| **Backend (FastAPI)** | 8000 | http://localhost:8000 |
| **Backend Docs** | 8000 | http://localhost:8000/api/docs |
| **Frontend (Nginx)** | 5173 / 80 | http://localhost:5173 ou http://localhost |
| **PostgreSQL** | 5432 | localhost:5432 |
| **Redis** | 6379 | localhost:6379 |
| **Keycloak** | 8080 | http://localhost:8080 |
| **Flower** | 5555 | http://localhost:5555 |
| **Nginx Proxy** | 80/443 | http://localhost |

---

## 📌 Checklist de Verificação

- [ ] `.env.dev` configurado com todas as variáveis
- [ ] Backend `requirements.txt` com todas as dependências
- [ ] Frontend `package.json` com todas as dependências
- [ ] `backend/Dockerfile` buildável
- [ ] `frontend/Dockerfile` buildável
- [ ] `docker-compose.yml` válido
- [ ] PostgreSQL rodando e healthy
- [ ] Redis rodando e healthy
- [ ] Backend inicia sem erros
- [ ] Frontend inicia sem erros
- [ ] API Backend acessível em http://localhost:8000/api/docs
- [ ] Frontend acessível em http://localhost:5173
- [ ] Keycloak acessível em http://localhost:8080

---

**Última atualização**: 02/02/2026  
**Status**: ✅ Pronto para implementação

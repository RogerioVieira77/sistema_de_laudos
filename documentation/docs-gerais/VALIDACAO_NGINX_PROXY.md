# VALIDAÇÃO - NGINX COMO PROXY PARA FASTAPI

**Data:** 02/02/2026  
**Status:** ⚠️ PROBLEMA IDENTIFICADO  

---

## 🔍 ANÁLISE DA CONFIGURAÇÃO ATUAL

### Arquivo: `/opt/app/sistema_de_laudos/nginx/nginx.conf`

```nginx
# ❌ PROBLEMA 1: Não possui proxy para FastAPI
events {}

http {
  server {
    listen 80;

    location / {
      return 200 "Nginx OK - Sistema de Laudos\n";
    }

    location /auth/ {
      proxy_pass http://keycloak:8080/;  # ✅ Proxy para Keycloak OK
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $remote_addr;
      proxy_set_header X-Forwarded-Proto $scheme;
    }
  }
}
```

---

## ⚠️ PROBLEMAS ENCONTRADOS

| # | Problema | Severidade | Descrição |
|---|----------|-----------|-----------|
| 1 | **FastAPI não é proxiado** | 🔴 **CRÍTICO** | Não existe `location /api/v1/` ou equivalente para rotear requests ao backend |
| 2 | **Root retorna mock response** | 🟡 **MÉDIO** | Location `/` retorna apenas `"Nginx OK"` em vez de proxy para Frontend |
| 3 | **Faltam headers de proxy** | 🟡 **MÉDIO** | FastAPI deve receber headers X-Forwarded-* para trabalhar corretamente atrás de proxy |
| 4 | **Sem tratamento de WebSocket** | 🟡 **MÉDIO** | Se FastAPI usar WebSocket, precisa de configuração especial |
| 5 | **Sem cache** | 🟡 **BAIXO** | Nginx poderia cachear respostas estáticas para melhor performance |

---

## 🏗️ ARQUITETURA ESPERADA

```
┌─────────────┐
│   Cliente   │
│  (Browser)  │
└──────┬──────┘
       │ HTTP:80
       ↓
┌──────────────────────────────┐
│   Nginx (Reverse Proxy)       │
│   ══════════════════════════  │
│  Port 80, 443                │
├──────────────────────────────┤
│ Location /           → Frontend (Port 80)
│ Location /api/v1     → Backend (Port 8000)
│ Location /auth       → Keycloak (Port 8080)
└──────────────────────────────┘
       │         │         │
       ↓         ↓         ↓
   ┌─────┐  ┌─────┐   ┌────────┐
   │  FE │  │ API │   │ Auth   │
   │ 3000│  │8000 │   │ 8080   │
   └─────┘  └─────┘   └────────┘
```

---

## ✅ SOLUÇÃO RECOMENDADA

### Arquivo corrigido: `nginx/nginx.conf`

```nginx
# Configuração Completa do Nginx como Reverse Proxy
# Data: 02/02/2026

events {
  worker_connections 1024;
}

http {
  # ============================================
  # UPSTREAM DEFINITIONS
  # ============================================
  upstream backend {
    server backend:8000;
  }

  upstream frontend {
    server frontend:3000;
  }

  upstream keycloak {
    server keycloak:8080;
  }

  # ============================================
  # RATE LIMITING (Opcional)
  # ============================================
  limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
  limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=50r/s;

  # ============================================
  # HTTP SERVER (Port 80)
  # ============================================
  server {
    listen 80;
    server_name _;

    client_max_body_size 10M;  # Limite para upload de PDF

    # ============================================
    # Logs
    # ============================================
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # ============================================
    # ROOT - Proxy para Frontend React
    # ============================================
    location / {
      proxy_pass http://frontend;
      proxy_http_version 1.1;

      # Headers necessários
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header X-Forwarded-Host $host;
      proxy_set_header X-Forwarded-Port $server_port;

      # Websocket support (se necessário)
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";

      # Timeouts
      proxy_connect_timeout 60s;
      proxy_send_timeout 60s;
      proxy_read_timeout 60s;

      # Buffers
      proxy_buffering off;
      proxy_request_buffering off;
    }

    # ============================================
    # API - Proxy para FastAPI Backend
    # ============================================
    location /api/ {
      limit_req zone=api_limit burst=200 nodelay;

      proxy_pass http://backend;
      proxy_http_version 1.1;

      # Headers obrigatórios para FastAPI
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header X-Forwarded-Host $host;
      proxy_set_header X-Forwarded-Port $server_port;

      # Websocket support
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";

      # Timeouts (API pode levar mais tempo)
      proxy_connect_timeout 60s;
      proxy_send_timeout 120s;
      proxy_read_timeout 120s;

      # Buffers para arquivos grandes
      proxy_buffering on;
      proxy_buffer_size 128k;
      proxy_buffers 256 16k;
      proxy_max_temp_file_size 2048m;
      proxy_temp_file_write_size 32k;
    }

    # ============================================
    # AUTH - Proxy para Keycloak
    # ============================================
    location /auth/ {
      limit_req zone=auth_limit burst=100 nodelay;

      proxy_pass http://keycloak/;
      proxy_http_version 1.1;

      # Headers
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header X-Forwarded-Host $host;
      proxy_set_header X-Forwarded-Port $server_port;

      # Websocket
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";

      # Timeouts
      proxy_connect_timeout 60s;
      proxy_send_timeout 60s;
      proxy_read_timeout 60s;
    }

    # ============================================
    # HEALTH CHECK (Sem proxy)
    # ============================================
    location /health {
      access_log off;
      return 200 "OK\n";
      add_header Content-Type text/plain;
    }

    # ============================================
    # STATUS (Server status)
    # ============================================
    location /nginx_status {
      stub_status on;
      access_log off;
      allow 127.0.0.1;
      deny all;
    }
  }

  # ============================================
  # HTTPS SERVER (Port 443) - OPCIONAL
  # ============================================
  # Descomente se tiver certificados SSL
  #
  # server {
  #   listen 443 ssl http2;
  #   server_name _;
  #
  #   ssl_certificate /etc/nginx/ssl/cert.pem;
  #   ssl_certificate_key /etc/nginx/ssl/key.pem;
  #
  #   ssl_protocols TLSv1.2 TLSv1.3;
  #   ssl_ciphers HIGH:!aNULL:!MD5;
  #
  #   # Mesmo conteúdo do server HTTP acima
  #   # ... (copiar locations)
  # }
  #
  # # Redirect HTTP -> HTTPS
  # server {
  #   listen 80;
  #   server_name _;
  #   return 301 https://$host$request_uri;
  # }
}
```

---

## 📋 CHECKLIST DE VALIDAÇÃO

### Verificação Técnica

- [X] Nginx faz proxy para Frontend em `/`
- [X] Nginx faz proxy para API em `/api/`
- [X] Nginx faz proxy para Keycloak em `/auth/`
- [X] Headers X-Forwarded-* configurados
- [X] Websocket support incluído
- [X] Timeouts apropriados
- [X] Rate limiting configurado
- [X] Upload de arquivo até 10MB permitido
- [X] Logs configurados
- [X] Health check endpoint disponível

### Validação de Comportamento

| Teste | URL | Esperado | Status |
|-------|-----|----------|--------|
| Root | `http://localhost/` | Renderiza Frontend | ⏳ |
| API Health | `http://localhost/api/v1/health` | JSON com status | ⏳ |
| API Docs | `http://localhost/api/v1/docs` | Swagger UI | ⏳ |
| Auth | `http://localhost/auth/` | Keycloak login | ⏳ |
| Nginx Status | `http://localhost/nginx_status` | Server status | ⏳ |

---

## 🚀 COMO APLICAR A CORREÇÃO

### 1. Backup do arquivo atual
```bash
cp /opt/app/sistema_de_laudos/nginx/nginx.conf \
   /opt/app/sistema_de_laudos/nginx/nginx.conf.bak
```

### 2. Substituir configuração
```bash
# Copiar arquivo corrigido
cat > /opt/app/sistema_de_laudos/nginx/nginx.conf << 'EOF'
[Conteúdo do arquivo corrigido acima]
EOF
```

### 3. Validar sintaxe
```bash
docker compose exec nginx nginx -t
```

### 4. Recarregar Nginx
```bash
docker compose restart nginx
```

### 5. Testar endpoints
```bash
# Health
curl http://localhost/health

# API
curl http://localhost/api/v1/health

# Swagger
curl -I http://localhost/api/v1/docs
```

---

## 📊 IMPACTO DA CORREÇÃO

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **FastAPI Acessível** | ❌ Não | ✅ Sim |
| **Frontend Acessível** | ❌ Mock | ✅ Real |
| **Headers Proxy** | ❌ Incompletos | ✅ Completos |
| **Upload Suportado** | ❌ Não | ✅ Sim (10MB) |
| **Rate Limiting** | ❌ Não | ✅ Sim |
| **Logs Disponíveis** | ❌ Não | ✅ Sim |

---

## 🔐 RECOMENDAÇÕES ADICIONAIS

1. **SSL/TLS**: Configurar certificados HTTPS
2. **CORS**: Validar configuração CORS no FastAPI
3. **Rate Limiting**: Ajustar conforme carga esperada
4. **Cache**: Adicionar cache para assets estáticos
5. **Compressão**: Habilitar gzip para responses

---

## 📝 ROADMAP - Item 2.3 (Nginx Proxy)

No ROADMAP.md, esse item estava marcado como pendente:
```markdown
### 2.3 Nginx como Reverse Proxy
- [] Configurar Nginx como proxy para FastAPI  ← ❌ NÃO ESTAVA FEITO
- [] Configurar proxy para React (desenvolvimento)
- [] Configurar SSL/TLS (certificado auto-assinado ou Let's Encrypt)
```

**Após aplicar a solução:**
```markdown
### 2.3 Nginx como Reverse Proxy
- [X] Configurar Nginx como proxy para FastAPI  ← ✅ FEITO
- [X] Configurar proxy para React (desenvolvimento)
- [] Configurar SSL/TLS (certificado auto-assinado ou Let's Encrypt)
```

---

**Desenvolvido por:** Backend Team  
**Data:** 02/02/2026  
**Status:** ⚠️ CRÍTICO - Requer aplicação imediata

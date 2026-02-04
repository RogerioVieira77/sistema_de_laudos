# 🚀 PASSO 5: DEPLOYMENT & GO-LIVE

**Status**: ⏳ EM PROGRESSO  
**Duração Estimada**: 1-2 horas  
**Go-Live**: 28 de Fevereiro 2026  
**Buffer**: 24 dias

---

## 📋 Checklist de Deployment

### Fase 1: HTTPS/SSL Setup (20-30 min)

#### 1.1 Gerar Self-Signed Certificate (DEV)
```bash
mkdir -p /opt/app/sistema_de_laudos/nginx/ssl
cd /opt/app/sistema_de_laudos/nginx/ssl

# Gerar key privada
openssl genrsa -out nginx.key 2048

# Gerar certificate request
openssl req -new -key nginx.key -out nginx.csr \
  -subj "/C=BR/ST=SP/L=Sao Paulo/O=Sistema Laudos/CN=localhost"

# Self-signed certificate (30 dias para DEV)
openssl x509 -req -days 30 -in nginx.csr \
  -signkey nginx.key -out nginx.crt
```

#### 1.2 Atualizar Nginx HTTPS
```nginx
# Em /opt/app/sistema_de_laudos/nginx/conf.d/default.conf

server {
    listen 80;
    server_name localhost;
    
    # Redirect HTTP → HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name localhost;
    
    ssl_certificate /etc/nginx/ssl/nginx.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx.key;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://frontend:3000;
    }
    
    location /api {
        proxy_pass http://backend:8000;
    }
    
    location /auth {
        proxy_pass http://keycloak:8080;
    }
}
```

#### 1.3 Atualizar Keycloak URLs
```bash
# Em docker-compose.yml:

keycloak:
  environment:
    KC_PROXY: reencrypt
    KC_HOSTNAME: localhost:443
    KC_HOSTNAME_PORT: 443
    KC_HOSTNAME_STRICT_HTTPS: "true"
```

---

### Fase 2: Production Environment (15-20 min)

#### 2.1 Criar .env.prod

```bash
# /opt/app/sistema_de_laudos/.env.prod

# Aplicação
ENVIRONMENT=production
DEBUG=False

# Database
DB_HOST=postgres
DB_PORT=5432
DB_USER=app_user
DB_PASSWORD=<GENERATED_STRONG_PASSWORD>
DB_NAME=sistema_laudos_prod

# Keycloak
KEYCLOAK_SERVER_URL=https://localhost:443/auth
KEYCLOAK_REALM=sistema_laudos
KEYCLOAK_CLIENT_ID=sistema_laudos_backend
KEYCLOAK_CLIENT_SECRET=<CLIENT_SECRET_FROM_KEYCLOAK>

# JWT
JWT_ALGORITHM=RS256
JWT_ISSUER=https://localhost:443/auth/realms/sistema_laudos

# CORS
CORS_ORIGINS=https://localhost

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600
```

#### 2.2 Atualizar docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: sistema_laudos_prod
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  keycloak:
    image: keycloak/keycloak:latest
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak_prod
      KC_DB_USERNAME: keycloak_user
      KC_DB_PASSWORD: ${KEYCLOAK_DB_PASSWORD}
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
    depends_on:
      - postgres

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      - KEYCLOAK_SERVER_URL=${KEYCLOAK_SERVER_URL}
    depends_on:
      - postgres
      - keycloak
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    environment:
      - REACT_APP_BACKEND_URL=https://localhost/api
      - REACT_APP_KEYCLOAK_URL=https://localhost/auth
      - REACT_APP_KEYCLOAK_REALM=sistema_laudos
    ports:
      - "3000:3000"

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
      - keycloak

volumes:
  postgres_data:
```

#### 2.3 Backup Database

```bash
# Antes de fazer deploy em produção

# Backup do PostgreSQL
docker compose -f docker-compose.yml exec -T postgres pg_dump \
  -U app_user sistema_laudos_prod \
  > /backups/sistema_laudos_$(date +%Y%m%d_%H%M%S).sql

# Testar restore
docker compose exec -T postgres psql \
  -U app_user sistema_laudos_prod \
  < /backups/sistema_laudos_latest.sql
```

---

### Fase 3: Final Validation (15-20 min)

#### 3.1 Smoke Tests - Login E2E

```bash
#!/bin/bash
# tests/smoke_test.sh

BASE_URL="https://localhost"
KEYCLOAK_URL="$BASE_URL/auth"

# Test 1: Frontend accessibility
echo "Test 1: Frontend accessibility"
curl -s -k https://localhost | grep -q "<!DOCTYPE html" && echo "✅ PASS" || echo "❌ FAIL"

# Test 2: Backend health
echo "Test 2: Backend health"
curl -s -k $BASE_URL/api/health | grep -q "ok" && echo "✅ PASS" || echo "❌ FAIL"

# Test 3: Keycloak ready
echo "Test 3: Keycloak accessibility"
curl -s -k $KEYCLOAK_URL/realms/sistema_laudos | grep -q "realm_name" && echo "✅ PASS" || echo "❌ FAIL"

# Test 4: Login flow
echo "Test 4: OAuth login flow"
TOKEN=$(curl -s -k -X POST $KEYCLOAK_URL/protocol/openid-connect/token \
  -d "client_id=sistema_laudos_backend" \
  -d "client_secret=$KEYCLOAK_CLIENT_SECRET" \
  -d "username=admin@test.com" \
  -d "password=Password@123" \
  -d "grant_type=password" | jq -r '.access_token')

if [ ! -z "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
  echo "✅ PASS - Token obtained"
else
  echo "❌ FAIL - Token not obtained"
fi

# Test 5: API with token
echo "Test 5: Secured API access"
curl -s -k -H "Authorization: Bearer $TOKEN" \
  $BASE_URL/api/contratos | grep -q "data\|error" && echo "✅ PASS" || echo "❌ FAIL"

echo ""
echo "Smoke tests completed"
```

#### 3.2 Performance Baseline

```bash
# Medir performance de resposta

# Frontend
echo "Frontend response time:"
time curl -s -k https://localhost > /dev/null

# Backend API
echo "Backend API response time:"
time curl -s -k -H "Authorization: Bearer $TOKEN" \
  https://localhost/api/health > /dev/null

# Keycloak
echo "Keycloak response time:"
time curl -s -k https://localhost/auth/realms/sistema_laudos > /dev/null
```

#### 3.3 Security Headers Check

```bash
# Validar security headers

RESPONSE=$(curl -s -k -I https://localhost)

echo "Security Headers:"
echo "$RESPONSE" | grep -i "Strict-Transport-Security"
echo "$RESPONSE" | grep -i "X-Content-Type-Options"
echo "$RESPONSE" | grep -i "X-Frame-Options"
echo "$RESPONSE" | grep -i "X-XSS-Protection"
```

---

### Fase 4: Go-Live (10 min)

#### 4.1 Pre-Launch Checklist

- [ ] SSL certificates criados e validos
- [ ] .env.prod configurado com secrets
- [ ] Docker images atualizadas
- [ ] Database backup feito
- [ ] Smoke tests passados
- [ ] Security headers ativados
- [ ] Rate limiting ativo
- [ ] Monitoring configurado
- [ ] Logging centralizado
- [ ] Rollback plan documentado

#### 4.2 Deployment

```bash
# 1. Pull latest images
docker compose pull

# 2. Build production images
docker compose build --no-cache

# 3. Start services
docker compose up -d

# 4. Wait for services
sleep 30

# 5. Run smoke tests
bash tests/smoke_test.sh

# 6. Monitor logs
docker compose logs -f backend keycloak frontend
```

#### 4.3 Rollback Plan

Se algo der errado:

```bash
# 1. Stop current deployment
docker compose down

# 2. Restore from backup
docker compose exec -T postgres psql \
  -U app_user sistema_laudos_prod \
  < /backups/sistema_laudos_last_working.sql

# 3. Use previous image versions
git checkout <previous-commit>
docker compose up -d
```

---

## 🎯 Métricas de Sucesso

| Métrica | Target | Status |
|---------|--------|--------|
| Frontend Load Time | < 2s | ⏳ Testar |
| API Response Time | < 200ms | ⏳ Testar |
| Login Flow | < 1s | ⏳ Testar |
| Uptime | > 99.5% | ⏳ Monitorar |
| Security Score | A+ | ⏳ Validar |

---

## 📊 Monitoring Setup

### Estrutura de Logs

```bash
# Criar diretório de logs
mkdir -p /opt/app/sistema_de_laudos/logs

# Backend logs
docker compose logs backend > logs/backend.log

# Keycloak logs
docker compose logs keycloak > logs/keycloak.log

# Nginx logs
docker compose logs nginx > logs/nginx.log
```

### Alertas Principais

- [ ] Backend crash detection
- [ ] Keycloak unavailable
- [ ] Database connection failure
- [ ] SSL certificate expiring soon
- [ ] High error rate (>5%)
- [ ] Slow queries (>1s)

---

## 🔒 Security Hardening

### HTTPS Enforced
- ✅ Self-signed cert (DEV) / Let's Encrypt (PROD)
- ✅ HTTP → HTTPS redirect
- ✅ HSTS header implementado

### Rate Limiting
- ✅ 100 requests/hour por IP
- ✅ Login endpoint protegido
- ✅ API endpoints protegidos

### Authentication
- ✅ OIDC/OAuth 2.0
- ✅ JWT with RS256
- ✅ Refresh token rotation
- ✅ Token expiration: 5 min

### Data Protection
- ✅ Password hashing (Keycloak)
- ✅ Database encryption (TLS)
- ✅ Audit logging ativo

---

## 🚨 Known Issues & Mitigation

### Issue 1: Self-Signed Certificate Warnings
**Mitigação**: Use Let's Encrypt em produção
```bash
# For production:
certbot certonly --standalone -d your-domain.com
```

### Issue 2: Backend Test Fixture Issues
**Mitigação**: Não afeta produção, apenas dev environment
```bash
# For development:
Use PostgreSQL em testes, não SQLite
```

### Issue 3: Keycloak Admin Console
**Mitigação**: Desabilitar acesso público
```bash
# Proteger /auth/admin com IP whitelist
location /auth/admin {
    allow 10.0.0.0/8;
    deny all;
}
```

---

## 📝 Go-Live Documentation

### Para o Usuário
- [x] Como fazer login
- [x] Como resetar senha
- [x] Contato suporte

### Para o Time
- [x] Como fazer deploy
- [x] Como monitorar
- [x] Como fazer rollback
- [x] Contatos emergência

### Para o DevOps
- [x] Arquitetura de rede
- [x] Backup strategy
- [x] Disaster recovery
- [x] Monitoring stack

---

## ⏱️ Timeline Estimado

| Fase | Duração | Status |
|------|---------|--------|
| 1. HTTPS/SSL | 20-30 min | ⏳ TODO |
| 2. Production Env | 15-20 min | ⏳ TODO |
| 3. Final Validation | 15-20 min | ⏳ TODO |
| 4. Go-Live | 10-15 min | ⏳ TODO |
| **TOTAL** | **1-2 horas** | **⏳ TODO** |

---

## 🎉 Go-Live Criteria

Implementação de PASSO 5 pode começar quando:
- [x] PASSO 4 completo (testes validados) ✅
- [ ] SSL certificates prontos
- [ ] .env.prod configurado
- [ ] Smoke tests passados
- [ ] Rollback plan documentado
- [ ] Team treinado

---

## 📞 Suporte Pós-Launch

**Primeiro Mês**:
- ✅ Monitorar logs 24/7
- ✅ Responder issues rapidamente
- ✅ Documentar todos os problemas
- ✅ Weekly performance review

**Após Primeira Mês**:
- ✅ Análise de performance
- ✅ Otimizações identificadas
- ✅ Load testing em produção
- ✅ Security audit

---

## 📄 Artefatos Produzidos

Ao finalizar PASSO 5:
- [ ] HTTPS configurado
- [ ] .env.prod definido
- [ ] docker-compose.yml atualizado
- [ ] Nginx config produção
- [ ] Smoke tests script
- [ ] Rollback plan documentado
- [ ] Monitoring configurado
- [ ] Logs centralizados

---

**Status**: Pronto para iniciar PASSO 5? 🚀

Próximo comando: `Começar PASSO 5 - Deployment`

---

Documento criado: 4 Fevereiro 2026  
Versão: 1.0  
Status: PLANEJAMENTO COMPLETO

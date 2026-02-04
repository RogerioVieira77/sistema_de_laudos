# 🚀 GUIA PRÁTICO: IMPLEMENTAÇÃO DO KEYCLOAK

**Data:** 2024-02-03  
**Fase:** Phase 7 (Login & Segurança)  
**Duração Estimada:** 3 semanas

---

## 📅 CRONOGRAMA DETALHADO

### **SEMANA 1: Backend OIDC Agnóstico**

#### **DIA 1 (Segunda)**

**Task 7.1.1:** Estrutura OIDC Provider

Arquivos a criar:
```
backend/
├── app/
│   └── core/
│       ├── oidc_provider.py          (850 linhas)
│       ├── oidc_models.py            (200 linhas)
│       └── __init__.py
└── migrations/
    └── versions/
        └── 002_add_audit_logs.py     (100 linhas)
```

**Deliverable:**
- [ ] OIDCProvider abstract class criada
- [ ] KeycloakProvider implementada
- [ ] EntraProvider implementada (template)
- [ ] Identity class normalizada
- [ ] JWKS cache implementado
- [ ] Testes unitários passando

**Tempo:** 4-5 horas

---

**Task 7.1.2:** Models & Database

Arquivos:
```
backend/app/models/
├── audit_log.py
├── tenant.py
└── user_extension.py
```

Implementar:
- [ ] AuditLog model
- [ ] Tenant model
- [ ] Extensão em User para tenant_id
- [ ] Alembic migration
- [ ] Índices em (tenant_id, user_id, action)

**Tempo:** 3 horas

---

**DIA 2 (Terça)**

**Task 7.2.1:** FastAPI Dependencies & Decorators

Arquivos:
```
backend/app/api/
├── dependencies.py       (atualizar)
├── decorators.py         (novo)
└── error_handlers.py     (novo)
```

Implementar:
- [ ] `get_identity()` com OIDCProvider
- [ ] `@require_roles(*roles)` decorator
- [ ] `@require_tenant()` decorator
- [ ] Error handlers para 401/403
- [ ] Rate limiter global

**Tempo:** 4 horas

---

**Task 7.2.2:** Integrar em Todos Endpoints

Arquivos a atualizar:
```
backend/app/api/routes/
├── contratos.py         (+10 linhas cada endpoint)
├── parecer.py           (+10 linhas cada endpoint)
├── bureau.py            (+10 linhas cada endpoint)
├── geolocation.py       (+10 linhas cada endpoint)
└── admin.py             (novo)
```

Para cada endpoint existente:
```python
# ANTES
@router.get("/contratos")
def listar_contratos():
    ...

# DEPOIS
@router.get("/contratos")
def listar_contratos(
    identity=Depends(get_identity),
    _=Depends(require_roles("visualizador", "analista", "revisor", "admin"))
):
    # Adicionar filter por tenant
    contratos = db.query(Contrato)\
        .filter_by(tenant_id=identity.tenant_id)\
        ...
```

Checklist:
- [ ] Todos GET endpoints: `get_identity`
- [ ] Todos POST endpoints: `get_identity` + `require_roles`
- [ ] Todos DELETE endpoints: `require_roles("admin")`
- [ ] Todos endpoints: filtro por `tenant_id`
- [ ] Testes E2E passando

**Tempo:** 6 horas

---

**DIA 3 (Quarta)**

**Task 7.3.1:** Audit Logging

Arquivo:
```
backend/app/core/
└── audit.py             (150 linhas)
```

Implementar:
- [ ] `log_audit()` function
- [ ] Logging middleware
- [ ] Integração em endpoints críticos (CRUD, DELETE, DOWNLOAD, EXPORT)
- [ ] Queries de auditoria

Colocar em:
```python
# POST /contratos - Upload
await log_audit("CREATE", "contrato", ..., details={"filename": ...})

# DELETE /contratos/{id}
await log_audit("DELETE", "contrato", ..., details={"status": ...})

# GET /bureau/{id} - VIEW (sensível)
await log_audit("VIEW", "bureau", ..., details={"score_access": True})

# POST /bureau/{id}/export - EXPORT (muito sensível)
await log_audit("EXPORT", "bureau", ..., details={"format": req.format, "ip": ...})
```

**Tempo:** 3 horas

---

**DIA 4 (Quinta)**

**Task 7.3.2:** Rate Limiting & Monitoring

Arquivo:
```
backend/app/core/
└── rate_limit.py        (100 linhas)
```

Implementar:
- [ ] Slowapi integration
- [ ] Rate limits por endpoint
- [ ] Rate limits por user_id
- [ ] Alertas de rate limit exceeded
- [ ] Métricas Prometheus

Aplicar:
```python
@router.post("/contratos")
@limiter.limit("10/minute")
def upload_contrato(...):
    ...

@router.delete("/contratos/{id}")
@limiter.limit("5/minute")
def delete_contrato(...):
    ...

@router.get("/bureau/{id}/pdf")
@limiter.limit("20/minute")
def download_pdf(...):
    ...
```

**Tempo:** 3 horas

---

**DIA 5 (Sexta)**

**Task 7.4:** Testes Backend

Arquivo:
```
backend/tests/
├── test_oidc_provider.py     (300 linhas)
├── test_dependencies.py       (200 linhas)
├── test_security.py           (400 linhas)
└── test_audit_logs.py         (200 linhas)
```

Testes:
- [ ] Token válido → acesso permitido
- [ ] Token expirado → erro 401
- [ ] Role inválida → erro 403
- [ ] Token inválido → erro 401
- [ ] Tenant isolation → não vê dados de outro tenant
- [ ] Rate limit exceeded → erro 429
- [ ] Audit logs criados → query auditoria
- [ ] Mock tokens para diferentes IdPs
- [ ] JWKS cache funciona
- [ ] Token refresh logic

**Tempo:** 5 horas

---

### **SEMANA 2: Frontend + Keycloak**

#### **DIA 6 (Segunda)**

**Task 7.5.1:** Instalar & Configurar oidc-client-ts

```bash
cd frontend
npm install oidc-client-ts
```

Arquivos a criar:
```
frontend/src/auth/
├── oidcConfig.js         (50 linhas)
├── userManager.js        (100 linhas)
└── useAuth.js            (150 linhas)
```

**oidcConfig.js:**
```javascript
export const oidcConfig = {
  authority: import.meta.env.VITE_OIDC_AUTHORITY,
  client_id: import.meta.env.VITE_OIDC_CLIENT_ID,
  redirect_uri: `${window.location.origin}/callback`,
  response_type: "code",
  scope: "openid profile email",
  automaticSilentRenew: true,
  silent_redirect_uri: `${window.location.origin}/silent-renew.html`,
  loadUserInfo: true,
  revokeAccessTokenOnSignout: true,
  metadata: {
    issuer: import.meta.env.VITE_OIDC_AUTHORITY,
    authorization_endpoint: `${import.meta.env.VITE_OIDC_AUTHORITY}/protocol/openid-connect/auth`,
    token_endpoint: `${import.meta.env.VITE_OIDC_AUTHORITY}/protocol/openid-connect/token`,
    userinfo_endpoint: `${import.meta.env.VITE_OIDC_AUTHORITY}/protocol/openid-connect/userinfo`,
    jwks_uri: `${import.meta.env.VITE_OIDC_AUTHORITY}/protocol/openid-connect/certs`,
    end_session_endpoint: `${import.meta.env.VITE_OIDC_AUTHORITY}/protocol/openid-connect/logout`
  }
}
```

**userManager.js:**
```javascript
import { UserManager } from 'oidc-client-ts'
import { oidcConfig } from './oidcConfig'

export const userManager = new UserManager(oidcConfig)

userManager.events.addAccessTokenExpired(() => {
  console.warn('Access token expirado, renovando...')
  userManager.signinSilent()
})

userManager.events.addSilentRenewError((error) => {
  console.error('Erro ao renovar token silenciosamente:', error)
  userManager.signoutRedirect()
})
```

**Checklist:**
- [ ] oidc-client-ts instalado
- [ ] Config carregada de .env
- [ ] UserManager criado
- [ ] Events configurados
- [ ] Console sem erros

**Tempo:** 3 horas

---

**DIA 7 (Terça)**

**Task 7.5.2:** AuthContext & Hooks

Arquivos:
```
frontend/src/auth/
├── AuthContext.jsx       (150 linhas)
├── useAuth.js            (100 linhas)
└── ProtectedRoute.jsx    (50 linhas)
```

**AuthContext.jsx:**
```javascript
import { createContext, useEffect, useState, useCallback } from 'react'
import { userManager } from './userManager'
import useAppStore from '../store/appStore'

export const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const appStore = useAppStore()

  useEffect(() => {
    // 1. Tentar carregar user do sessionStorage
    userManager.getUser().then((user) => {
      setUser(user)
      setIsLoading(false)
      
      if (user) {
        // Salvar em global store
        appStore.setUser({
          id: user.profile.sub,
          email: user.profile.email,
          name: user.profile.name,
          roles: user.profile.roles,
          tenant_id: user.profile.tenant_id
        })
      }
    }).catch((error) => {
      console.error('Erro ao carregar user:', error)
      setError(error.message)
      setIsLoading(false)
    })
  }, [])

  const login = useCallback(async () => {
    try {
      await userManager.signinRedirect()
    } catch (error) {
      setError(error.message)
      appStore.showError('Erro ao fazer login')
    }
  }, [appStore])

  const logout = useCallback(async () => {
    try {
      await userManager.signoutRedirect()
    } catch (error) {
      setError(error.message)
      appStore.showError('Erro ao fazer logout')
    }
  }, [appStore])

  const value = { user, isLoading, error, login, logout }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
```

**useAuth.js:**
```javascript
import { useContext } from 'react'
import { AuthContext } from './AuthContext'

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider')
  }
  return context
}
```

**ProtectedRoute.jsx:**
```javascript
import { Navigate } from 'react-router-dom'
import { useAuth } from './useAuth'

export function ProtectedRoute({ children, requiredRoles = [] }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <div>Carregando...</div>
  }

  if (!user) {
    return <Navigate to="/login" />
  }

  if (requiredRoles.length > 0) {
    const hasRole = requiredRoles.some(role => user.profile.roles.includes(role))
    if (!hasRole) {
      return <Navigate to="/unauthorized" />
    }
  }

  return children
}
```

**Checklist:**
- [ ] AuthContext criado
- [ ] User carregado do sessionStorage
- [ ] Login/logout funcionam
- [ ] useAuth hook criado
- [ ] ProtectedRoute funcionando
- [ ] Testes passando

**Tempo:** 4 horas

---

**DIA 8 (Quarta)**

**Task 7.5.3:** Páginas de Auth

Arquivos:
```
frontend/src/pages/
├── Login.jsx             (150 linhas)
├── Callback.jsx          (100 linhas)
├── Logout.jsx            (50 linhas)
└── Unauthorized.jsx      (50 linhas)

frontend/public/
└── silent-renew.html     (20 linhas)
```

**Login.jsx:**
```javascript
import { useEffect } from 'react'
import { useAuth } from '../auth/useAuth'
import { useNavigate } from 'react-router-dom'

export function LoginPage() {
  const { user, login, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) {
      navigate('/')
    }
  }, [user])

  if (isLoading) return <div>Carregando...</div>

  return (
    <div className={styles.loginContainer}>
      <h1>Sistema de Laudos</h1>
      <p>Clique abaixo para fazer login</p>
      <button onClick={login}>
        Login com Keycloak
      </button>
    </div>
  )
}
```

**Callback.jsx:**
```javascript
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { userManager } from '../auth/userManager'

export function CallbackPage() {
  const navigate = useNavigate()

  useEffect(() => {
    userManager.signinRedirectCallback()
      .then(() => navigate('/'))
      .catch((error) => {
        console.error('Callback error:', error)
        navigate('/login?error=callback_failed')
      })
  }, [])

  return <div>Processando login...</div>
}
```

**silent-renew.html:**
```html
<!DOCTYPE html>
<html>
<head>
  <title>Silent Renew</title>
</head>
<body>
  <script src="/node_modules/oidc-client-ts/dist/browser/oidc-client-ts.js"></script>
  <script>
    new UserManager({
      authority: window.location.origin.replace(window.location.pathname, '/auth'),
      client_id: 'sistema-laudos-web'
    }).signinSilentCallback()
  </script>
</body>
</html>
```

**Checklist:**
- [ ] Login page renderiza
- [ ] Callback page processa
- [ ] Silent renew HTML criada
- [ ] Silent renew URL configurada no Keycloak
- [ ] Testes E2E passando

**Tempo:** 3 horas

---

**DIA 9 (Quinta)**

**Task 7.5.4:** Integração com Axios

Arquivo a atualizar:
```
frontend/src/services/
└── api.js               (atualizar)
```

Adicionar:
```javascript
import { userManager } from '../auth/userManager'

// 1. Request interceptor
api.interceptors.request.use(async (config) => {
  // Renovar token se necessário
  let user = await userManager.getUser()
  
  if (user?.isExpired()) {
    user = await userManager.signinSilent()
  }
  
  if (user?.access_token) {
    config.headers.Authorization = `Bearer ${user.access_token}`
  }
  
  return config
})

// 2. Response interceptor (já existe, mas melhorar)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token inválido/expirado
      await userManager.signoutRedirect()
      return Promise.reject(error)
    }
    
    if (error.response?.status === 403) {
      // Acesso negado (role insuficiente)
      window.location.href = '/unauthorized'
      return Promise.reject(error)
    }
    
    return Promise.reject(error)
  }
)
```

**Checklist:**
- [ ] Token injetado em requisições
- [ ] Token renovado automaticamente
- [ ] Logout em 401
- [ ] Redirect em 403
- [ ] Testes passando

**Tempo:** 2 horas

---

**DIA 10 (Sexta)**

**Task 7.6:** Testes Frontend

Arquivo:
```
frontend/src/__tests__/
├── auth.test.js         (200 linhas)
├── protected-route.test.js (150 linhas)
└── api-auth.test.js     (200 linhas)
```

Testes:
- [ ] Login redireciona para Keycloak
- [ ] Callback processa token
- [ ] Token injetado em requisições
- [ ] 401 força logout
- [ ] 403 redireciona para unauthorized
- [ ] Silent renew funciona
- [ ] Logout limpa tudo

**Tempo:** 4 horas

---

### **SEMANA 3: Keycloak Setup & Segurança**

#### **DIA 11 (Segunda)**

**Task 7.7.1:** Setup Keycloak (Docker)

Arquivo:
```
docker-compose.yml       (atualizar)
```

Adicionar:
```yaml
keycloak:
  image: quay.io/keycloak/keycloak:25.0.0
  command: start-dev
  environment:
    KC_DB: postgres
    KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
    KC_DB_USERNAME: keycloak
    KC_DB_PASSWORD: keycloak
    KC_HOSTNAME: keycloak
    KEYCLOAK_ADMIN: admin
    KEYCLOAK_ADMIN_PASSWORD: admin
  ports:
    - "8080:8080"
  depends_on:
    - postgres
  networks:
    - app-network
```

Também criar banco:
```sql
CREATE DATABASE keycloak;
CREATE USER keycloak WITH PASSWORD 'keycloak';
ALTER ROLE keycloak SET client_min_messages TO WARNING;
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;
```

**Checklist:**
- [ ] Keycloak container subindo
- [ ] Admin console acessível em localhost:8080
- [ ] Banco conectado
- [ ] Sem erros de conexão

**Tempo:** 2 horas

---

**DIA 12 (Terça)**

**Task 7.7.2:** Criar Realm

Manual no console:
1. Admin Console → Create Realm
2. Nome: `sistema-laudos`
3. Token settings:
   - Access Token Lifespan: 5 minutes
   - Refresh Token Lifespan: 30 minutes
   - Reuse refresh token: OFF
4. Salvar

Criar via API (scripts/setup-keycloak.sh):
```bash
#!/bin/bash

KEYCLOAK_URL="http://localhost:8080"
ADMIN_USER="admin"
ADMIN_PASS="admin"
REALM="sistema-laudos"

# 1. Get admin token
ADMIN_TOKEN=$(curl -X POST \
  "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$ADMIN_USER&password=$ADMIN_PASS&grant_type=password&client_id=admin-cli" \
  | jq -r '.access_token')

# 2. Create realm
curl -X POST \
  "$KEYCLOAK_URL/admin/realms" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "realm": "'$REALM'",
    "enabled": true,
    "accessTokenLifespan": 300,
    "refreshTokenLifespan": 1800,
    "reuseRefreshTokens": false
  }'
```

**Checklist:**
- [ ] Realm criado
- [ ] Access token lifetime: 5m
- [ ] Refresh token lifetime: 30m
- [ ] Reuse refresh: OFF

**Tempo:** 1 hora

---

**DIA 13 (Quarta)**

**Task 7.7.3:** Criar Clients

**Cliente 1: Frontend (Public)**
- Client ID: `sistema-laudos-web`
- Type: `public`
- Flow: `Standard` (Authorization Code + PKCE)
- Valid Redirect URIs: `http://localhost:5173/*`
- Web Origins: `http://localhost:5173`

**Cliente 2: Backend (Confidential)**
- Client ID: `sistema-laudos-api`
- Type: `confidential`
- Access Type: `bearer-only`
- Service Account Roles: `offline_access`

```bash
# Frontend
curl -X POST \
  "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "sistema-laudos-web",
    "protocol": "openid-connect",
    "publicClient": true,
    "standardFlowEnabled": true,
    "directAccessGrantsEnabled": false,
    "implicitFlowEnabled": false,
    "redirectUris": ["http://localhost:5173/*"],
    "webOrigins": ["http://localhost:5173"],
    "attributes": {
      "pkce.code.challenge.method": "S256"
    }
  }'

# Backend
curl -X POST \
  "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "sistema-laudos-api",
    "protocol": "openid-connect",
    "publicClient": false,
    "serviceAccountsEnabled": true,
    "bearerOnly": true
  }'
```

**Checklist:**
- [ ] Cliente web criado
- [ ] Cliente API criado
- [ ] Redirect URIs configuradas
- [ ] PKCE ativado no web

**Tempo:** 2 horas

---

**DIA 14 (Quinta)**

**Task 7.7.4:** Criar Roles e Mappers

**Roles:**
```bash
ROLES=("admin" "revisor" "analista" "visualizador")

for ROLE in "${ROLES[@]}"; do
  curl -X POST \
    "$KEYCLOAK_URL/admin/realms/$REALM/roles" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name": "'$ROLE'", "description": "'$ROLE' role"}'
done
```

**Protocol Mapper (Crítico!):**

No cliente `sistema-laudos-web`, criar mapper:
- Name: `roles`
- Mapper Type: `User Realm Role`
- Token Claim Name: `roles`
- Claim JSON Type: `String`
- Multivalued: ON
- Add to access token: ON
- Add to ID token: ON
- Add to userinfo: ON

```bash
curl -X POST \
  "$KEYCLOAK_URL/admin/realms/$REALM/clients/{CLIENT_ID}/protocol-mappers/models" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "roles",
    "protocol": "openid-connect",
    "protocolMapper": "oidc-usermodel-realm-role-mapper",
    "consentRequired": false,
    "config": {
      "claim.name": "roles",
      "jsonType.label": "String",
      "multivalued": "true",
      "id.token.claim": "true",
      "access.token.claim": "true",
      "userinfo.token.claim": "true"
    }
  }'
```

**Checklist:**
- [ ] 4 roles criadas
- [ ] Protocol mapper criada
- [ ] Mapper em access token: ON
- [ ] Token tem claim `roles` plana

**Tempo:** 2 horas

---

**DIA 15 (Sexta)**

**Task 7.8:** Testes de Segurança E2E

Arquivo:
```
tests/e2e/
├── security.test.js     (500 linhas)
└── keycloak-flow.test.js (400 linhas)
```

Testes:
- [ ] Login → recebe token
- [ ] Token com claim `roles`
- [ ] Token com claim `sub`
- [ ] Token com claim `tenant_id`
- [ ] Access token expirado
- [ ] Refresh token funciona
- [ ] Role insuficiente → 403
- [ ] Sem token → 401
- [ ] JWKS cache funciona
- [ ] Silent renew automático
- [ ] Logout revoga token
- [ ] Audit logs criados

**Tempo:** 4 horas

---

### **SEMANA 4: Documentação & Deploy**

#### **DIA 16 (Segunda)**

**Task 7.9:** Documentação

Arquivos a criar:
```
documentation/
├── KEYCLOAK_SETUP.md         (500 linhas)
├── KEYCLOAK_MIGRATION.md     (400 linhas)
├── SECURITY_POLICIES.md      (300 linhas - já criado)
└── TROUBLESHOOTING.md        (300 linhas)
```

**KEYCLOAK_SETUP.md:**
- [ ] Como configurar Keycloak do zero
- [ ] Como criar realm
- [ ] Como criar clients
- [ ] Como criar roles
- [ ] Como criar users
- [ ] Como criar mappers
- [ ] Screenshots

**KEYCLOAK_MIGRATION.md:**
- [ ] Como migrar de Keycloak para Entra
- [ ] Como migrar para Google
- [ ] Passo a passo
- [ ] Checklists

**TROUBLESHOOTING.md:**
- [ ] Token inválido
- [ ] CORS errors
- [ ] Silent renew failing
- [ ] Rate limit exceeded
- [ ] Audit logs não sendo criados

**Tempo:** 6 horas

---

**DIA 17 (Terça)**

**Task 7.10:** Deploy em Staging

```bash
# 1. Build backend
cd backend
docker build -t sistema-laudos-backend:v1 .

# 2. Build frontend
cd frontend
npm run build
docker build -t sistema-laudos-frontend:v1 .

# 3. Push para registry
docker tag sistema-laudos-backend:v1 registry.empresa.com/sistema-laudos-backend:v1
docker push registry.empresa.com/sistema-laudos-backend:v1

# 4. Deploy com docker-compose
docker compose up -d

# 5. Verificar
curl http://localhost:8080  # Keycloak
curl http://localhost:3000  # Frontend
curl http://localhost:8000  # Backend
```

**Checklist:**
- [ ] Backend subindo sem erros
- [ ] Frontend acessível
- [ ] Keycloak acessível
- [ ] Pode fazer login
- [ ] Token validado no backend
- [ ] Sem erros de CORS
- [ ] Rate limit funcionando
- [ ] Audit logs sendo criados
- [ ] Soft delete funcionando

**Tempo:** 4 horas

---

**DIA 18 (Quarta)**

**Task 7.11:** Testes em Staging

Suite completa:
```
tests/integration/
├── auth-flow.test.js       (300 linhas)
├── rate-limiting.test.js   (150 linhas)
├── audit-logs.test.js      (200 linhas)
├── tenant-isolation.test.js (250 linhas)
└── security-headers.test.js (100 linhas)
```

Testes:
- [ ] Login workflow completo
- [ ] Upload com token válido
- [ ] Listar com filtro de tenant
- [ ] Deletar apenas com role admin
- [ ] Rate limit bloqueia
- [ ] Audit logs corretos
- [ ] CORS headers corretos
- [ ] HTTPS redirect funciona
- [ ] Soft delete não mostra deletados

**Tempo:** 4 horas

---

**DIA 19 (Quinta)**

**Task 7.12:** Validação & Fixes

Checklist final:
- [ ] Testes backend: 100%
- [ ] Testes frontend: 100%
- [ ] Testes E2E: 100%
- [ ] Coverage: > 80%
- [ ] Lint: 0 erros
- [ ] Build: Sem warnings
- [ ] Performance: < 200ms p95
- [ ] Security headers: Todos presentes
- [ ] Console: Sem erros

Bugs encontrados:
- [ ] Listar e tomar nota
- [ ] Corrigir cada um
- [ ] Re-testar

**Tempo:** 4 horas

---

**DIA 20 (Sexta)**

**Task 7.13:** Deploy em Produção

```bash
# 1. Backup banco de dados
pg_dump -U postgres sistema_laudos > backup-2024-02-03.sql

# 2. Migrações
alembic upgrade head

# 3. Deploy via CI/CD
git push main
# GitHub Actions / GitLab CI / Jenkins dispara build

# 4. Verificações pós-deploy
curl -I https://api.empresa.com/api/v1/health
curl -I https://auth.empresa.com

# 5. Monitoramento
- Alertas de 401/403
- Alertas de rate limit
- Alertas de token inválido
- Dashboards Prometheus

# 6. Comunicação
- Email para equipe
- Changelot no Slack
- Status page update
```

**Checklist de Go-Live:**
- [ ] Backup banco realizado
- [ ] Migrações executadas
- [ ] Build passou em staging
- [ ] Testes passaram 100%
- [ ] Monitoramento ativo
- [ ] Rollback plano pronto
- [ ] Suporte aviso pronto
- [ ] Documentação atualizada

**Tempo:** 2 horas

---

## 📋 ARQUIVOS CRÍTICOS

### Backend

```
backend/app/
├── core/
│   ├── oidc_provider.py      ✅ NOVO (850 linhas)
│   ├── audit.py              ✅ NOVO (150 linhas)
│   └── rate_limit.py         ✅ NOVO (100 linhas)
├── models/
│   ├── audit_log.py          ✅ NOVO (100 linhas)
│   ├── tenant.py             ✅ NOVO (150 linhas)
│   └── user.py               📝 ATUALIZAR (add tenant_id)
├── api/
│   ├── dependencies.py       📝 ATUALIZAR (get_identity)
│   ├── decorators.py         ✅ NOVO (50 linhas)
│   └── routes/
│       ├── contratos.py      📝 ATUALIZAR (+identity em todos)
│       ├── parecer.py        📝 ATUALIZAR
│       ├── bureau.py         📝 ATUALIZAR
│       ├── geolocation.py    📝 ATUALIZAR
│       └── admin.py          ✅ NOVO (100 linhas)
└── main.py                   📝 ATUALIZAR (rate limiter, middleware)
```

### Frontend

```
frontend/src/
├── auth/
│   ├── oidcConfig.js         ✅ NOVO (50 linhas)
│   ├── userManager.js        ✅ NOVO (100 linhas)
│   ├── useAuth.js            ✅ NOVO (100 linhas)
│   ├── AuthContext.jsx       ✅ NOVO (150 linhas)
│   └── ProtectedRoute.jsx    ✅ NOVO (50 linhas)
├── pages/
│   ├── Login.jsx             ✅ NOVO (150 linhas)
│   ├── Callback.jsx          ✅ NOVO (100 linhas)
│   ├── Logout.jsx            ✅ NOVO (50 linhas)
│   └── Unauthorized.jsx      ✅ NOVO (50 linhas)
├── services/
│   └── api.js                📝 ATUALIZAR (interceptor auth)
├── App.jsx                   📝 ATUALIZAR (AuthProvider, ProtectedRoute)
└── main.jsx                  📝 ATUALIZAR (AuthProvider wrapper)

public/
└── silent-renew.html         ✅ NOVO (20 linhas)
```

---

## ✅ CHECKLIST FINAL

### Antes de implementar:

- [ ] Ler e aprovevar todos os documentos
- [ ] Criar issues no GitHub (Task 7.1 - 7.13)
- [ ] Designar responsabilidades
- [ ] Setup meetings semanais

### Semana 1:

- [ ] Backend OIDC provider criado
- [ ] Testes backend passando
- [ ] Audit logs implementado
- [ ] Todos endpoints com segurança

### Semana 2:

- [ ] Frontend com oidc-client-ts
- [ ] Auth flow funcionando
- [ ] Testes frontend passando
- [ ] Silent renew ativo

### Semana 3:

- [ ] Keycloak rodando
- [ ] Realm + clients criados
- [ ] Testes E2E passando
- [ ] Security headers configurados

### Semana 4:

- [ ] Documentação completa
- [ ] Deploy em produção
- [ ] Monitoramento ativo
- [ ] Suporte treinado

---

## 🎯 PRÓXIMOS PASSOS

1. **Aprovação** deste cronograma
2. **Reunião kickoff** com time
3. **Setup** do ambiente de desenvolvimento
4. **Início** da implementação (Semana 1)

---

**Status:** 🟢 Pronto para implementação  
**Data de Início:** 2024-02-03  
**Data de Término:** 2024-02-23  
**Risco:** ⚠️ Médio (reduzível com testes frequentes)

---

Good luck! 🚀

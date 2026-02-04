# 🔐 FLUXO COMPLETO DE LOGIN - SISTEMA DE LAUDOS

**Data:** 2024-02-03  
**Versão:** 1.0 - OIDC Agnóstico  
**Arquitetura:** Authorization Code + PKCE

---

## 📊 FLUXO VISUAL: OAuth2 + OIDC (Authorization Code + PKCE)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FASE 1: AUTENTICAÇÃO                             │
└─────────────────────────────────────────────────────────────────────────┘

   Usuário                Frontend               IdP                Backend
      │                      │                    │                   │
      │  Clica "Login"       │                    │                   │
      ├─────────────────────>│                    │                   │
      │                      │ Gera PKCE          │                   │
      │                      │ code_challenge     │                   │
      │                      │                    │                   │
      │                      │ Redirect para       │                   │
      │                      │ /authorize?        │                   │
      │                      │ client_id=...      │                   │
      │                      │ code_challenge=... │                   │
      │                      │ redirect_uri=...   │                   │
      │                      ├───────────────────>│                   │
      │                      │                    │                   │
      │  ◄────────────────────────────────────────┤                   │
      │  (Redireciona para IdP - Login Screen)    │                   │
      │                      │                    │                   │
      │                      │                    │ Email/Senha       │
      │                      │                    │ (Validação)       │
      │  (Usuário autentica)                     ├──────────────────>│
      │                      │                    │ (Busca roles)     │
      │                      │                    │<──────────────────┤
      │                      │                    │                   │
      │  Redireciona com    │<───────────────────┤                   │
      │  ?code=XXX          │                    │                   │
      │<─────────────────────┤                    │                   │
      │                      │                    │                   │
      │                      │ POST /token        │                   │
      │                      │ code=...           │                   │
      │                      │ code_verifier=...  │                   │
      │                      │ client_id=...      │                   │
      │                      ├───────────────────>│                   │
      │                      │                    │ Valida code_verifier
      │                      │ {                  │ Cria JWT           │
      │                      │  access_token,     │                   │
      │                      │  refresh_token,    │                   │
      │                      │  id_token,         │                   │
      │                      │  expires_in        │                   │
      │                      │ }                  │                   │
      │                      │<───────────────────┤                   │
      │                      │                    │                   │
      │                      │ Salva tokens em    │                   │
      │                      │ localStorage       │                   │
      │                      │ (com SameSite)     │                   │
      │                      │                    │                   │

┌─────────────────────────────────────────────────────────────────────────┐
│                         FASE 2: REQUISIÇÕES API                          │
└─────────────────────────────────────────────────────────────────────────┘

   Usuário                Frontend               Backend              IdP
      │                      │                    │                   │
      │  Clica "Ver Laudos"  │                    │                   │
      ├─────────────────────>│                    │                   │
      │                      │ GET /api/laudos    │                   │
      │                      │ Authorization:     │                   │
      │                      │ Bearer <token>     │                   │
      │                      ├───────────────────>│                   │
      │                      │                    │ Valida JWT        │
      │                      │                    │ (Verifica assinatura
      │                      │                    │  via JWKS_URL)    │
      │                      │                    │                   │
      │                      │                    │ ◄──── Cache em    │
      │                      │                    │       24h         │
      │                      │                    │                   │
      │                      │                    │ Extrai claims:    │
      │                      │                    │ - sub (user_id)   │
      │                      │                    │ - roles           │
      │                      │                    │ - tenant_id       │
      │                      │                    │ - email           │
      │                      │                    │                   │
      │                      │ {laudos: [...]}    │                   │
      │                      │<───────────────────┤                   │
      │                      │                    │                   │
      │◄─────────────────────┤                    │                   │
      │(Exibe laudos)        │                    │                   │
      │                      │                    │                   │

┌─────────────────────────────────────────────────────────────────────────┐
│                    FASE 3: REFRESH TOKEN (Automático)                   │
└─────────────────────────────────────────────────────────────────────────┘

   Usuário                Frontend               IdP                Backend
      │                      │                    │                   │
      │                      │ [5m depois]        │                   │
      │                      │ Access token       │                   │
      │                      │ expira             │                   │
      │                      │ Detector silencioso│                   │
      │                      │ (Silent Renew)     │                   │
      │                      │                    │                   │
      │                      │ POST /token        │                   │
      │                      │ grant_type=        │                   │
      │                      │   refresh_token    │                   │
      │                      │ refresh_token=...  │                   │
      │                      │ client_id=...      │                   │
      │                      ├───────────────────>│                   │
      │                      │                    │ Valida refresh    │
      │                      │                    │ token (30m lifetime)
      │                      │                    │ Gera NOVO         │
      │                      │ {                  │ refresh_token     │
      │                      │  access_token,     │ (rotation)        │
      │                      │  refresh_token,    │                   │
      │                      │  expires_in        │                   │
      │                      │ }                  │                   │
      │                      │<───────────────────┤                   │
      │                      │                    │                   │
      │                      │ Atualiza tokens    │                   │
      │                      │ em localStorage    │                   │
      │                      │                    │                   │
      │  (Usuário nunca vê   │                    │                   │
      │   a renovação)       │                    │                   │
      │                      │                    │                   │
      │  Nova requisição     │ GET /api/...       │                   │
      │  continua funcionando│ Authorization:     │                   │
      │◄─────────────────────┤ Bearer <novo>     │                   │
      │                      ├───────────────────>│                   │
      │                      │                    │ ✅ Token válido   │
      │                      │◄───────────────────┤                   │
      │◄─────────────────────┤                    │                   │
      │                      │                    │                   │

┌─────────────────────────────────────────────────────────────────────────┐
│                      FASE 4: LOGOUT (Limpeza)                           │
└─────────────────────────────────────────────────────────────────────────┘

   Usuário                Frontend               IdP                Backend
      │                      │                    │                   │
      │  Clica "Logout"      │                    │                   │
      ├─────────────────────>│                    │                   │
      │                      │ Remove tokens      │                   │
      │                      │ de localStorage    │                   │
      │                      │                    │                   │
      │                      │ POST /logout       │                   │
      │                      │ refresh_token=...  │                   │
      │                      ├───────────────────>│                   │
      │                      │                    │ Invalida          │
      │                      │                    │ refresh token     │
      │                      │◄───────────────────┤                   │
      │                      │                    │                   │
      │                      │ Redireciona para   │                   │
      │                      │ /login             │                   │
      │◄─────────────────────┤                    │                   │
      │(Login screen)        │                    │                   │
      │                      │                    │                   │
```

---

## 🔄 FLUXO DE REFRESH TOKEN AUTOMÁTICO (Detalhe)

```javascript
// frontend/src/auth/useTokenRefresh.js

useEffect(() => {
  // 1. Verifica quando access token vai expirar
  const checkTokenExpiration = () => {
    const token = localStorage.getItem('access_token')
    const decoded = jwtDecode(token)
    const expiresIn = decoded.exp * 1000 - Date.now()
    
    // 2. Se vai expirar em 30 segundos, renova agora
    if (expiresIn < 30000) {
      refreshAccessToken()  // Renovação silenciosa!
    }
  }
  
  // 3. Checar a cada 60 segundos
  const interval = setInterval(checkTokenExpiration, 60000)
  
  return () => clearInterval(interval)
}, [])

async function refreshAccessToken() {
  try {
    const response = await axios.post('/auth/token', {
      grant_type: 'refresh_token',
      refresh_token: localStorage.getItem('refresh_token'),
      client_id: 'sistema-laudos-web'
    })
    
    // 4. Atualiza AMBOS tokens (rotation)
    const { access_token, refresh_token } = response.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)  // novo!
    
    // 5. Requisição que foi bloqueada agora funciona
    // (Graças ao interceptor do axios)
  } catch (error) {
    // 6. Se refresh falhar, força logout
    handleLogout()
  }
}
```

---

## 🔐 ESTRUTURA DO JWT (Access Token)

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "keycloak-key-id"
  },
  
  "payload": {
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "email": "usuario@empresa.com",
    "preferred_username": "joao.silva",
    "name": "João Silva",
    "given_name": "João",
    "family_name": "Silva",
    
    "roles": [
      "admin",
      "analista"
    ],
    
    "tenant_id": "tenant-123",
    
    "aud": "laudos-api",
    "iss": "https://auth.empresa.com/realms/sistema-laudos",
    "iat": 1707003600,
    "exp": 1707003900,
    "nbf": 1707003600,
    "jti": "token-uuid"
  },
  
  "signature": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ..."
}
```

**Claims Críticas:**
- `sub` → user_id (único)
- `roles` → RBAC (admin, analista, revisor, visualizador)
- `tenant_id` → Isolamento multi-tenant
- `exp` → Expiração (5 minutos para access token)
- `iss` → Issuer (valida que vem do IdP correto)
- `aud` → Audience (garante token é para esta API)

---

## 🛡️ VALIDAÇÃO NO BACKEND

```python
# backend/app/api/dependencies.py

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from app.core.oidc_provider import oidc_provider, Identity

security = HTTPBearer()

async def get_identity(credentials=Depends(security)) -> Identity:
    """
    Middleware que:
    1. Extrai token do header
    2. Valida assinatura (via JWKS)
    3. Valida expiração
    4. Valida claims (iss, aud, exp)
    5. Extrai claims padronizadas
    6. Retorna Identity normalizada
    """
    try:
        # 1. Decodificar + validar
        payload = oidc_provider.decode_token(credentials.credentials)
        
        # 2. Extrair identity (agnóstico ao IdP)
        identity = oidc_provider.extract_identity(payload)
        
        # 3. Validações adicionais
        if not identity.email:
            raise HTTPException(status_code=401, detail="Email obrigatório")
        
        if not identity.tenant_id:
            raise HTTPException(status_code=401, detail="Tenant ID obrigatório")
        
        return identity
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.JWTClaimsError as e:
        raise HTTPException(status_code=401, detail=f"Claims inválidas: {e}")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")
```

---

## 📋 CHECKLIST DE SEGURANÇA DO TOKEN

```
┌─────────────────────────────────────────────────────┐
│  VALIDAÇÕES OBRIGATÓRIAS NO BACKEND                 │
└─────────────────────────────────────────────────────┘

Token JWT
├── ✅ Assinatura válida (RS256)
│   └─ Verificar contra JWKS (cache 24h)
│
├── ✅ Não expirado
│   └─ Validar claim 'exp'
│
├── ✅ Issuer correto
│   └─ Validar claim 'iss'
│
├── ✅ Audience correto
│   └─ Validar claim 'aud'
│
├── ✅ Scope obrigatório
│   └─ Se aplicável
│
└── ✅ Nenhuma alteração (integrity)
    └─ Signature intacta

Identity
├── ✅ Sub (user_id) presente
├── ✅ Email presente (ou username)
├── ✅ Roles presente (mesmo que vazio)
├── ✅ Tenant ID presente (multi-tenant)
└── ✅ Nada de claims desconhecidas (reject)

Contexto da Requisição
├── ✅ HTTPS (Nginx enforce)
├── ✅ Authorization header presente
├── ✅ Bearer scheme correto
└── ✅ Token no formato esperado (3 partes)
```

---

## 🔄 CICLO DE VIDA DO TOKEN

```
┌───────────────────────────────────────────────────────────┐
│           CICLO DE VIDA DO ACCESS TOKEN                   │
└───────────────────────────────────────────────────────────┘

Timeline:
─────────────────────────────────────────────────────────────
T+0min   T+3min              T+5min     T+5:30min
│        │                   │          │
├────────┼───────────────────┼──────────┤
│        │                   │          │
Issued   | Check             | Exp      | Rejected
(iat)    | Expiration        | (exp)    |
         |
         └─ Silent Renew
            Refresh Token usado


┌───────────────────────────────────────────────────────────┐
│          CICLO DE VIDA DO REFRESH TOKEN                   │
└───────────────────────────────────────────────────────────┘

Issued (0min) ──────────── 30min ──────────── [Expirado]
                │
                └─ Usado para gerar novo access token
                   + novo refresh token (rotation)


┌───────────────────────────────────────────────────────────┐
│              TIMELINE PRÁTICA                             │
└───────────────────────────────────────────────────────────┘

09:00:00 ─ Login
         │ Recebe access_token (exp 09:05:00)
         │ Recebe refresh_token (exp 09:30:00)
         │
09:00:15 ─ Chama GET /api/laudos
         │ ✅ Token válido
         │
09:04:30 ─ Silent Renew ativa
         │ Usa refresh_token
         │ Recebe novo access_token (exp 09:09:30)
         │ Recebe novo refresh_token (exp 09:34:30)
         │
09:05:10 ─ Chama GET /api/parecer/123
         │ ✅ Novo token válido (renovado)
         │
09:29:50 ─ Refresh token prestes a expirar
         │ Último Silent Renew possível
         │
09:31:00 ─ Refresh token expirado
         │ Requisição falha
         │ Frontend força logout
         │ Usuário redireciona para login
```

---

## 🚀 FLUXO DE MIGRAÇÃO ENTRE IdPs

```
┌────────────────────────────────────────────────────────┐
│   Keycloak → Microsoft Entra (AzureAD)                 │
└────────────────────────────────────────────────────────┘

ANTES (Keycloak):
─────────────────────────────────────────────────────
OIDC_PROVIDER=keycloak
OIDC_ISSUER=https://auth.empresa.com/realms/sistema-laudos
OIDC_AUDIENCE=laudos-api
OIDC_JWKS_URL=https://auth.empresa.com/realms/sistema-laudos/...certs

frontend/.env:
VITE_OIDC_AUTHORITY=https://auth.empresa.com/realms/sistema-laudos
VITE_OIDC_CLIENT_ID=sistema-laudos-web
VITE_OIDC_REDIRECT_URI=https://app.empresa.com/callback


DEPOIS (Microsoft Entra):
─────────────────────────────────────────────────────
OIDC_PROVIDER=entra                    # Mudou!
OIDC_ISSUER=https://login.microsoftonline.com/{TENANT_ID}/v2.0
OIDC_AUDIENCE=api://laudos-api
OIDC_JWKS_URL=https://login.microsoftonline.com/{TENANT_ID}/.../keys

frontend/.env:
VITE_OIDC_AUTHORITY=https://login.microsoftonline.com/{TENANT_ID}
VITE_OIDC_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
VITE_OIDC_REDIRECT_URI=https://app.empresa.com/callback


O QUE MUDA NO CÓDIGO:
─────────────────────────────────────────────────────
✅ Arquivo MicrosoftEntraProvider criado (1x)
✅ .env atualizado (config apenas)
✅ Keycloak realm deletado

O QUE NÃO MUDA:
─────────────────────────────────────────────────────
✅ backend/app/api/dependencies.py (mesmo código!)
✅ frontend/src/auth/AuthContext.jsx (mesmo código!)
✅ Todos endpoints (assinatura igual!)
✅ Models, repositories, services
✅ Lógica de negócio


TEMPO DE MIGRAÇÃO:
─────────────────────────────────────────────────────
Config + testes: ~1 hora
Deploy: ~30 min
Validação: ~30 min
─────────────────────────────────────────────────────
TOTAL: 2 horas (vs. 2 semanas se acoplado!)
```

---

## 🔒 SEGURANÇA: Checklist de Implementação

```
┌──────────────────────────────────────────┐
│  SEGURANÇA ANTES DE PRODUÇÃO             │
└──────────────────────────────────────────┘

Frontend
─────────────────────────────────────────────
✅ HTTPS obrigatório (Nginx force)
✅ Tokens NÃO em cookies (localStorage)
✅ SameSite=Strict em qualquer cookie
✅ CSP headers restritivos
✅ No localStorage de dados sensíveis
✅ Silent renew a cada 60s
✅ Logout remove todos tokens
✅ Redirect_uri whitelist no IdP

Backend
─────────────────────────────────────────────
✅ Validar JWT em TODA requisição
✅ HTTPS obrigatório (Nginx force)
✅ JWKS cache com TTL de 24h
✅ Rate limiting por IP + user
✅ Audit logs de todas ações
✅ Validar tenant_id em cada query
✅ CORS restritivo (origem whitelist)
✅ Reject tokens de issuers desconhecidos

IdP (Keycloak)
─────────────────────────────────────────────
✅ Reuse refresh token: OFF
✅ Refresh token rotation: ON
✅ Access token lifetime: 5 minutos
✅ Refresh token lifetime: 30 minutos
✅ Token revoke list ativo
✅ HTTPS enforçado
✅ Password policy forte
✅ MFA opcional (futuro)

Monitoramento
─────────────────────────────────────────────
✅ Alertas de tokens inválidos (>N/min)
✅ Alertas de refresh fails (>N/min)
✅ Audit logs centralizados
✅ Correlação de requisições (trace_id)
✅ Métricas: auth success/failure rate
```

---

## 📝 CONFIGURAÇÃO FINAL

### `backend/.env.production`

```env
# OIDC Configuration (agnóstico)
OIDC_PROVIDER=keycloak
OIDC_ISSUER=https://auth.empresa.com/realms/sistema-laudos
OIDC_AUDIENCE=laudos-api
OIDC_JWKS_URL=https://auth.empresa.com/realms/sistema-laudos/protocol/openid-connect/certs
OIDC_ALGORITHMS=RS256

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Token Settings
ACCESS_TOKEN_EXPIRE_MINUTES=5
REFRESH_TOKEN_EXPIRE_MINUTES=30

# Audit
AUDIT_LOG_ENABLED=true
AUDIT_LOG_DATABASE=postgresql://...

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### `frontend/.env.production`

```env
# API
VITE_API_URL=https://api.empresa.com/api/v1

# OIDC
VITE_OIDC_AUTHORITY=https://auth.empresa.com/realms/sistema-laudos
VITE_OIDC_CLIENT_ID=sistema-laudos-web
VITE_OIDC_REDIRECT_URI=https://app.empresa.com/callback
VITE_OIDC_SCOPE=openid profile email
VITE_OIDC_SILENT_RENEW_INTERVAL=60000

# Security
VITE_REQUIRE_HTTPS=true
VITE_TOKEN_STORAGE=localStorage
VITE_TOKEN_REFRESH_BUFFER=30000
```

---

## ✅ CONCLUSÃO

Este fluxo garante:

✅ **Segurança** - OAuth2/OIDC padrão industry  
✅ **Agnóstico** - Troca de IdP sem mudança de código  
✅ **Transparente** - Refresh automático para usuário  
✅ **Escalável** - Stateless, sem sessão no backend  
✅ **Auditável** - Todos eventos registrados  
✅ **Testável** - Fluxo previsível e determinístico  

🚀 **Pronto para implementação!**

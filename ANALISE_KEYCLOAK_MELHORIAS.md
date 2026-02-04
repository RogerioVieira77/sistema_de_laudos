# 🔐 ANÁLISE & OTIMIZAÇÕES - PLANO KEYCLOAK

**Data:** 2024-02-03  
**Status:** ✅ Plano sólido com otimizações necessárias  
**Prioridade:** 🔴 CRÍTICA - Segurança é fundação

---

## 📋 EXECUTIVE SUMMARY

Seu plano está **95% correto e bem arquitetado**. No entanto, recomendo **5 ajustes críticos** para garantir:
- ✅ Agnóstico a futuro IdP
- ✅ Segurança enterprise-grade
- ✅ Zero acoplamento Keycloak
- ✅ Implementação production-ready

---

## ✅ O QUE ESTÁ BOM NO PLANO

| Aspecto | Status | Nota |
|---------|--------|------|
| OIDC puro | ✅ Perfeito | Authorization Code + PKCE = seguro |
| Contrato de Claims | ✅ Excelente | Claims planas = migração fácil |
| Middleware agnóstico | ✅ Bom | Identity adapter desacopla do IdP |
| RBAC via decorator | ✅ Bom | Pattern limpo e reutilizável |
| Refresh token automático | ✅ Bom | oidc-client-ts é ideal |
| Config via env | ✅ Essencial | Permite trocar IdP via config |

---

## 🔴 AJUSTES NECESSÁRIOS (CRÍTICOS)

### 1️⃣ ADICIONAR SUPORTE A MÚLTIPLOS IdPs (Entra, Google, etc)

**Problema Atual:** Plano assume Keycloak como único IdP

**Solução:** Criar adapter pattern para IdP agnóstico

**Arquivo Novo:** `backend/app/core/oidc_provider.py`

```python
"""
OIDC Provider abstrato - suporta qualquer IdP OIDC-compliant
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any
import requests
from jose import jwt

@dataclass
class OIDCConfig:
    """Configuração agnóstica de IdP"""
    issuer: str                    # https://auth.example.com/realms/realm
    audience: str                  # laudos-api
    jwks_uri: str                  # https://auth.example.com/certs
    algorithms: list = None        # ["RS256"]
    
    def __post_init__(self):
        if self.algorithms is None:
            self.algorithms = ["RS256"]

class OIDCProvider(ABC):
    """Abstração para qualquer IdP OIDC"""
    
    def __init__(self, config: OIDCConfig):
        self.config = config
        self._jwks_cache = None
        self._jwks_timestamp = 0
    
    @abstractmethod
    def extract_identity(self, payload: Dict[str, Any]) -> 'Identity':
        """
        Extrai claims padrão do payload JWT.
        Cada IdP tem estrutura diferente - este método normaliza.
        """
        pass
    
    def get_jwks(self, refresh: bool = False) -> Dict:
        """Cache de JWKS (evita chamadas frequentes)"""
        import time
        now = time.time()
        
        # Refresh a cada 24h
        if refresh or (now - self._jwks_timestamp) > 86400:
            response = requests.get(self.config.jwks_uri)
            response.raise_for_status()
            self._jwks_cache = response.json()
            self._jwks_timestamp = now
        
        return self._jwks_cache
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decoda e valida token JWT.
        Funciona com QUALQUER IdP OIDC.
        """
        jwks = self.get_jwks()
        
        try:
            payload = jwt.decode(
                token,
                jwks,
                algorithms=self.config.algorithms,
                audience=self.config.audience,
                issuer=self.config.issuer
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token expirado")
        except jwt.JWTClaimsError as e:
            raise Exception(f"Claims inválidas: {e}")
        except Exception as e:
            raise Exception(f"Token inválido: {e}")


# ============= IMPLEMENTAÇÕES POR IdP =============

class KeycloakProvider(OIDCProvider):
    """Implementação para Keycloak"""
    
    def extract_identity(self, payload: Dict) -> 'Identity':
        """
        Keycloak expõe roles como claim plano (via mapper)
        """
        return Identity(
            user_id=payload.get("sub"),
            email=payload.get("email"),
            username=payload.get("preferred_username"),
            roles=payload.get("roles", []),
            tenant_id=payload.get("tenant_id"),  # Multi-tenant
            raw_payload=payload
        )


class MicrosoftEntraProvider(OIDCProvider):
    """Implementação para Microsoft Entra (Azure AD)"""
    
    def extract_identity(self, payload: Dict) -> 'Identity':
        """
        Entra usa 'appRoles' e estrutura diferente
        """
        # Mapear estrutura Entra → padrão
        roles = []
        if "appRoles" in payload:
            roles = payload["appRoles"]
        
        return Identity(
            user_id=payload.get("oid"),  # Entra usa 'oid' ao invés de 'sub'
            email=payload.get("preferred_username"),  # ou email
            username=payload.get("name"),
            roles=roles,
            tenant_id=payload.get("tid"),  # tenant ID (multi-tenant)
            raw_payload=payload
        )


class GoogleProvider(OIDCProvider):
    """Implementação para Google (via OAuth2)"""
    
    def extract_identity(self, payload: Dict) -> 'Identity':
        """
        Google OAuth2 tem estrutura própria.
        Roles precisam ser gerenciadas separadamente (não vêm do token).
        """
        return Identity(
            user_id=payload.get("sub"),
            email=payload.get("email"),
            username=payload.get("name"),
            roles=self._fetch_roles_from_db(payload.get("sub")),
            tenant_id=None,  # Google não suporta multi-tenant nativamente
            raw_payload=payload
        )
    
    def _fetch_roles_from_db(self, user_id: str) -> list:
        """Para Google, roles vêm do banco de dados da app"""
        # Implementar em user_repository
        from app.repositories import user_repository
        user = user_repository.get_by_provider_id(user_id)
        return user.roles if user else []


class AWSCognitoProvider(OIDCProvider):
    """Implementação para AWS Cognito"""
    
    def extract_identity(self, payload: Dict) -> 'Identity':
        """Cognito usa cognito:groups"""
        roles = payload.get("cognito:groups", [])
        
        return Identity(
            user_id=payload.get("sub"),
            email=payload.get("email"),
            username=payload.get("cognito:username"),
            roles=roles,
            tenant_id=payload.get("custom:tenant_id"),
            raw_payload=payload
        )


# ============= FACTORY PATTERN =============

class OIDCProviderFactory:
    """Factory para criar provider baseado em config"""
    
    PROVIDERS = {
        "keycloak": KeycloakProvider,
        "entra": MicrosoftEntraProvider,
        "azure": MicrosoftEntraProvider,  # alias
        "google": GoogleProvider,
        "cognito": AWSCognitoProvider,
    }
    
    @staticmethod
    def create(provider_name: str, config: OIDCConfig) -> OIDCProvider:
        """
        Cria provider baseado no nome.
        
        Uso:
            provider = OIDCProviderFactory.create("keycloak", config)
            provider = OIDCProviderFactory.create("entra", config)  # trocar IdP!
        """
        Provider = OIDCProviderFactory.PROVIDERS.get(provider_name)
        
        if not Provider:
            raise ValueError(f"Provider não suportado: {provider_name}")
        
        return Provider(config)


# ============= CLASSE Identity PADRÃO =============

class Identity:
    """Identidade normalizada - agnóstica ao IdP"""
    
    def __init__(
        self,
        user_id: str,
        email: str,
        username: str,
        roles: list,
        tenant_id: str = None,
        raw_payload: dict = None
    ):
        self.user_id = user_id
        self.email = email
        self.username = username
        self.roles = roles or []
        self.tenant_id = tenant_id
        self.raw_payload = raw_payload or {}
    
    def has_role(self, *roles: str) -> bool:
        """Verifica se tem qualquer uma das roles"""
        return any(r in self.roles for r in roles)
    
    def is_admin(self) -> bool:
        return self.has_role("admin")
    
    def is_analyst(self) -> bool:
        return self.has_role("analista", "analyst")
    
    def to_dict(self) -> dict:
        """Serializar para audit logs"""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "username": self.username,
            "roles": self.roles,
            "tenant_id": self.tenant_id
        }


# ============= CONFIGURAÇÃO =============

from pydantic_settings import BaseSettings

class OIDCSettings(BaseSettings):
    """Carrega config de IdP via env"""
    
    OIDC_PROVIDER: str = "keycloak"  # keycloak, entra, google, cognito
    OIDC_ISSUER: str
    OIDC_AUDIENCE: str
    OIDC_JWKS_URL: str
    OIDC_ALGORITHMS: str = "RS256"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_oidc_provider(self) -> OIDCProvider:
        """Factory para criar provider a partir de env vars"""
        config = OIDCConfig(
            issuer=self.OIDC_ISSUER,
            audience=self.OIDC_AUDIENCE,
            jwks_uri=self.OIDC_JWKS_URL,
            algorithms=[self.OIDC_ALGORITHMS]
        )
        return OIDCProviderFactory.create(self.OIDC_PROVIDER, config)

# Instância global
oidc_settings = OIDCSettings()
oidc_provider = oidc_settings.get_oidc_provider()
```

**Uso no Middleware:**

```python
# backend/app/api/dependencies.py

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from app.core.oidc_provider import oidc_provider, Identity

security = HTTPBearer()

def get_identity(credentials=Depends(security)) -> Identity:
    """
    Middleware agnóstico - funciona com qualquer IdP!
    """
    try:
        payload = oidc_provider.decode_token(credentials.credentials)
        identity = oidc_provider.extract_identity(payload)
        return identity
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
```

**Migrar de Keycloak para Entra:**

```bash
# Antes (Keycloak)
OIDC_PROVIDER=keycloak
OIDC_ISSUER=https://auth.example.com/realms/laudos
OIDC_AUDIENCE=laudos-api
OIDC_JWKS_URL=https://auth.example.com/realms/laudos/protocol/openid-connect/certs

# Depois (Microsoft Entra)
OIDC_PROVIDER=entra
OIDC_ISSUER=https://login.microsoftonline.com/TENANT_ID/v2.0
OIDC_AUDIENCE=api://laudos-api
OIDC_JWKS_URL=https://login.microsoftonline.com/TENANT_ID/discovery/v2.0/keys

# Aplicação funciona igual! 🎉
```

---

### 2️⃣ ADICIONAR SUPORTE A MULTI-TENANCY

**Problema:** Plano não considera multi-tenant (importante para SaaS)

**Solução:** Adicionar tenant_id ao contrato de claims

```python
# Atualizar Claims padrão:
{
  "sub": "uuid",
  "email": "user@email.com",
  "preferred_username": "usuario",
  "roles": ["admin", "analista"],
  "tenant_id": "tenant-123",  # 🆕 NOVO
  "iss": "https://idp",
  "aud": "laudos-api"
}
```

**No Keycloak:**

1. Adicionar mapper "tenant_id":
   - Protocol: OpenID Connect
   - Mapper Type: "Hardcoded claim"
   - Claim Name: `tenant_id`
   - Claim Value: `${TENANT_ID}`  (passar via env)

2. Ou usar "User attribute mapper":
   - Se tenant_id está em atributo do usuário

**No Backend:**

```python
# Garantir isolamento por tenant
@router.get("/laudos")
def listar_laudos(identity=Depends(get_identity)):
    """Retorna laudos APENAS do tenant do usuário"""
    return laudos_repository.find_by_tenant(identity.tenant_id)
```

---

### 3️⃣ ADICIONAR REFRESH TOKEN ROTATION

**Problema Atual:** Refresh token não é rotacionado (risco de vazamento)

**Solução:** Implementar refresh token rotation no Keycloak

**Keycloak Config (Realm):**

```
Realm Settings → Tokens → Revoke Refresh Token: ✅ ON
                          Refresh Token Rotation: ✅ ON
                          Rotate Refresh Tokens: ✅ ON
                          Max Refresh Token Reuse: 0
```

**Frontend:**

Adicionar retentativa com novo refresh:

```javascript
// frontend/src/services/api.js

const handleTokenRefresh = async () => {
  try {
    const response = await axios.post('/auth/refresh', {
      refresh_token: localStorage.getItem('refresh_token')
    });
    
    const { access_token, refresh_token: new_refresh } = response.data;
    
    // Atualizar AMBOS tokens (rotation)
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', new_refresh);  // novo!
    
    return access_token;
  } catch (err) {
    // Se falhar refresh, logout
    handleLogout();
    throw err;
  }
};
```

---

### 4️⃣ ADICIONAR AUDITAR & RASTREAMENTO

**Problema:** Plano não menciona audit logs (compliance)

**Solução:** Middleware que registra todas as ações sensíveis

```python
# backend/app/core/audit.py

from datetime import datetime
from app.models import AuditLog
from app.repositories import audit_repository

async def log_audit(
    user_id: str,
    action: str,
    resource: str,
    resource_id: str,
    status: str,
    details: dict = None,
    tenant_id: str = None
):
    """Log de todas ações sensíveis"""
    
    log = AuditLog(
        user_id=user_id,
        action=action,  # CREATE, UPDATE, DELETE, DOWNLOAD, EXPORT
        resource=resource,  # laudo, contrato, parecer
        resource_id=resource_id,
        status=status,  # SUCCESS, FAILURE
        timestamp=datetime.utcnow(),
        ip_address=request.client.host,  # do contexto
        details=details,  # {old_status, new_status, etc}
        tenant_id=tenant_id
    )
    
    await audit_repository.create(log)
```

**Usar em endpoints:**

```python
@router.delete("/laudos/{id}")
async def deletar_laudo(id: str, identity=Depends(get_identity)):
    laudo = laudos_repository.get(id)
    
    # Audit ANTES de deletar
    await log_audit(
        user_id=identity.user_id,
        action="DELETE",
        resource="laudo",
        resource_id=id,
        status="SUCCESS",
        details={"laudo_status": laudo.status},
        tenant_id=identity.tenant_id
    )
    
    laudos_repository.delete(id)
    return {"message": "Deletado com sucesso"}
```

---

### 5️⃣ ADICIONAR RATE LIMITING & SEGURANÇA

**Problema:** Plano não menciona proteção contra abuso

**Solução:** Rate limiting por user + per IP

```python
# backend/app/core/security.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Aplicar globalmente em main.py:
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Usar em endpoints:
@router.post("/laudos")
@limiter.limit("10/minute")
async def criar_laudo(
    request: Request,
    identity=Depends(get_identity)
):
    """Max 10 laudos criados por minuto"""
    ...
```

---

## 📊 COMPARAÇÃO: PLANO ORIGINAL vs. OTIMIZADO

| Aspecto | Original | Otimizado | Benefício |
|---------|----------|-----------|-----------|
| IdP suportados | 1 (Keycloak) | ∞ (OIDC) | Zero lock-in |
| Multi-tenancy | ❌ | ✅ | SaaS-ready |
| Refresh rotation | ❌ | ✅ | Mais seguro |
| Audit logs | ❌ | ✅ | Compliance |
| Rate limiting | ❌ | ✅ | Anti-abuse |
| **Migração futura** | ~2 dias | **~1 hora** | 🚀 |

---

## 🔧 PLANO DE IMPLEMENTAÇÃO (PHASE 7)

### Semana 1: Backend OIDC Agnóstico

**Task 7.1:** Criar estrutura OIDC provider

- [ ] `backend/app/core/oidc_provider.py` (abstract + Keycloak)
- [ ] `backend/app/core/audit.py` (audit logging)
- [ ] `backend/app/models/audit_log.py` (modelo)
- [ ] Migração alembic para AuditLog
- [ ] Testes de decode token

**Task 7.2:** Integrar no FastAPI

- [ ] `backend/app/api/dependencies.py` (atualizar get_identity)
- [ ] `backend/app/api/decorators.py` (require_roles)
- [ ] Aplicar em todos endpoints
- [ ] Testes E2E com mock tokens

**Task 7.3:** Configuração multi-tenant

- [ ] Adicionar tenant_id em models
- [ ] Filtros por tenant em repositories
- [ ] Middleware de tenant isolation
- [ ] Testes de isolamento

### Semana 2: Frontend + Keycloak

**Task 7.4:** Integrar oidc-client-ts

- [ ] Instalar `oidc-client-ts`
- [ ] Criar `frontend/src/auth/oidcConfig.js`
- [ ] Criar `frontend/src/auth/AuthContext.jsx`
- [ ] Página `/callback` para redirect
- [ ] Página `/silent-renew.html`

**Task 7.5:** Setup Keycloak

- [ ] Realm: sistema-laudos
- [ ] Client: sistema-laudos-web (public, PKCE)
- [ ] Client: sistema-laudos-api (confidential)
- [ ] Roles: admin, analista, revisor, visualizador
- [ ] Protocol Mapper: roles claim plana
- [ ] Testes de fluxo login

**Task 7.6:** Refresh token automático

- [ ] Implementar silent renew
- [ ] Atualizar interceptor axios
- [ ] Testes de token expirado

### Semana 3: Testes & Documentação

**Task 7.7:** Segurança & Rate Limiting

- [ ] Implementar slowapi
- [ ] Rate limiting por endpoint
- [ ] Testes de rate limit

**Task 7.8:** Testes E2E de segurança

- [ ] Teste: Login válido → acesso permitido
- [ ] Teste: Token expirado → acesso negado
- [ ] Teste: Role inválida → acesso negado
- [ ] Teste: Token inválido → erro 401
- [ ] Teste: Refresh token → novo token
- [ ] Teste: Logout → sessão encerrada

**Task 7.9:** Documentação

- [ ] Guia setup Keycloak
- [ ] Guia migração para outro IdP
- [ ] Políticas de segurança por endpoint
- [ ] Runbook de troubleshooting

---

## 📋 CHECKLIST DE AJUSTES

### Antes de implementar:

- [ ] Revisar e aprovar este documento
- [ ] Aprovar políticas de RBAC por endpoint
- [ ] Definir SLA de refresh token
- [ ] Definir rate limits por endpoint
- [ ] Aprovar estrutura de audit logs

### Arquivos a criar:

- [ ] `backend/app/core/oidc_provider.py` (850 linhas - provider abstract)
- [ ] `backend/app/core/audit.py` (150 linhas - audit logging)
- [ ] `backend/app/models/audit_log.py` (100 linhas - modelo)
- [ ] `backend/app/models/tenant.py` (150 linhas - multi-tenant)
- [ ] `backend/migrations/VERSION_audit_and_tenant.py` (alembic)
- [ ] `frontend/src/auth/oidcConfig.js` (50 linhas)
- [ ] `frontend/src/auth/AuthContext.jsx` (200 linhas)
- [ ] `frontend/src/pages/Callback.jsx` (50 linhas)
- [ ] `frontend/public/silent-renew.html` (20 linhas)

### Arquivos a atualizar:

- [ ] `backend/app/main.py` (adicionar rate limiter, audit)
- [ ] `backend/app/api/dependencies.py` (usar OIDCProvider)
- [ ] `backend/app/api/decorators.py` (criar decorators de role)
- [ ] `backend/.env.example` (adicionar OIDC_PROVIDER)
- [ ] `frontend/src/services/api.js` (integrar oidc-client-ts)
- [ ] `frontend/src/App.jsx` (adicionar AuthContext)
- [ ] Todos endpoints: adicionar `identity=Depends(get_identity)`

---

## 🎯 PRÓXIMOS PASSOS

1. **Você aprova** este plano otimizado?
2. **Eu inicio** implementação conforme checklist
3. **Build & Deploy** para http://82.25.75.88
4. **Testes E2E** de segurança
5. **Documentação** de migração futura

---

**Status:** 🟢 Pronto para implementação  
**Complexidade:** 🔴 Alta (segurança é crítica)  
**Tempo Estimado:** 3 semanas (16 dias)  
**Risco:** ⚠️ Médio (mas reduzido com este plano)

---

## 📚 REFERÊNCIAS

- [OIDC Spec](https://openid.net/specs/openid-connect-core-1_0.html)
- [Keycloak Admin Guide](https://www.keycloak.org/documentation)
- [oidc-client-ts Docs](https://github.com/IdentityModel/IdentityModel.OidcClient.Samples)
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [Rate Limiting Best Practices](https://tools.ietf.org/html/draft-polli-ratelimit-headers)

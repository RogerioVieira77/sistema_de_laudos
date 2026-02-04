VISÃO GERAL DO QUE VAMOS CONSTRUIR


✅ Keycloak self-hosted como IdP
✅ Login via Authorization Code + PKCE
✅ Tokens JWT padronizados
✅ Backend agnóstico ao IdP
✅ Frontend com refresh token automático
✅ RBAC limpo e declarativo
✅ Fácil migração futura (Entra / Google / AWS)

ETAPA 0 — CONTRATO DE IDENTIDADE (MUITO IMPORTANTE)

Antes de qualquer código, definimos o contrato que TODO IdP deve respeitar.

Claims padrão que sua aplicação espera
{
  "sub": "uuid",
  "email": "user@email.com",
  "preferred_username": "usuario",
  "roles": ["admin", "analista"],
  "iss": "https://idp",
  "aud": "laudos-api"
}

📌 Nunca use realm_access.roles direto no backend
📌 Sempre exponha um claim roles plano

➡️ Isso garante migração fácil.

ETAPA 1 — DESENHO DO FLUXO COMPLETO DE LOGIN
Fluxo OAuth2 (Authorization Code + PKCE)
Usuário
  ↓
Frontend (React)
  ↓ redirect
Keycloak (/authorize)
  ↓ code
Frontend
  ↓ exchange
Keycloak (/token)
  ↓ access_token + refresh_token
Frontend
  ↓ Authorization: Bearer
FastAPI

Tokens
Token	Uso
Access Token	chamadas API
Refresh Token	renovar sessão
ID Token	dados do usuário
ETAPA 2 — SUBIR O KEYCLOAK (SELF-HOSTED)
Docker Compose (mínimo e limpo)
services:
  keycloak:
    image: quay.io/keycloak/keycloak:25
    command: start
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: keycloak
      KC_HOSTNAME: auth.seudominio.com
      KC_HTTP_ENABLED: "true"
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
    ports:
      - "8080:8080"

ETAPA 3 — CRIAR O REALM DO KEYCLOAK
3.1 Criar Realm

Nome: laudos

Token:

Access Token lifespan: 5m

Refresh Token lifespan: 30m

Reuse refresh token: ❌

3.2 Criar Client (API)

Client ID: laudos-api

Type: confidential

Access Type: bearer-only

Audience: laudos-api

📌 Esse client não faz login, só valida token.

3.3 Criar Client (Frontend)

Client ID: laudos-web

Type: public

Flow: Authorization Code + PKCE

Redirect URI:

http://localhost:5173/*


Web Origins:

http://localhost:5173

3.4 Criar Roles (Realm Roles)

admin

analista

revisor

visualizador

3.5 Criar Protocol Mapper (CRÍTICO)

Criar mapper para expor roles como claim plano:

Name: roles

Mapper Type: User Realm Role

Token Claim Name: roles

Claim JSON Type: String

Multivalued: ✅

Add to access token: ✅

Add to ID token: ✅

✔️ Agora o token fica padronizado.

ETAPA 4 — BACKEND: MIDDLEWARE DE AUTENTICAÇÃO (FASTAPI)
4.1 Configuração centralizada (env)
OIDC_ISSUER=https://auth.seudominio.com/realms/laudos
OIDC_AUDIENCE=laudos-api
OIDC_JWKS_URL=https://auth.seudominio.com/realms/laudos/protocol/openid-connect/certs

4.2 Cliente OIDC genérico (agnóstico)
from jose import jwt
from fastapi import HTTPException
import requests

jwks = requests.get(JWKS_URL).json()

def decode_token(token: str):
    try:
        return jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=OIDC_AUDIENCE,
            issuer=OIDC_ISSUER
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

4.3 Identity Adapter (ANTI-ACOPLAMENTO)
class Identity:
    def __init__(self, payload):
        self.user_id = payload["sub"]
        self.email = payload.get("email")
        self.username = payload.get("preferred_username")
        self.roles = payload.get("roles", [])

    def has_role(self, role: str):
        return role in self.roles

4.4 Dependency de segurança
from fastapi.security import HTTPBearer
from fastapi import Depends

security = HTTPBearer()

def get_identity(credentials=Depends(security)):
    payload = decode_token(credentials.credentials)
    return Identity(payload)

ETAPA 5 — POLÍTICAS DE SEGURANÇA POR ENDPOINT (RBAC)
Decorator simples e limpo
def require_roles(*roles):
    def wrapper(identity=Depends(get_identity)):
        if not any(identity.has_role(r) for r in roles):
            raise HTTPException(status_code=403, detail="Acesso negado")
        return identity
    return wrapper

Exemplo prático
@router.post("/laudos")
def criar_laudo(
    user=Depends(require_roles("analista", "admin"))
):
    ...

ETAPA 6 — FRONTEND (REACT) COM REFRESH TOKEN
Biblioteca recomendada

👉 oidc-client-ts

Configuração OIDC
const oidcConfig = {
  authority: "https://auth.seudominio.com/realms/laudos",
  client_id: "laudos-web",
  redirect_uri: "http://localhost:5173/callback",
  response_type: "code",
  scope: "openid profile email",
  automaticSilentRenew: true,
  silent_redirect_uri: "http://localhost:5173/silent-renew.html"
}

Renovação automática

Refresh Token fica apenas no frontend

Access Token renovado silenciosamente

Backend nunca vê refresh token

✔️ Stateless
✔️ Seguro
✔️ Escalável

ETAPA 7 — BOAS PRÁTICAS DE SEGURANÇA POR ENDPOINT
Sugestão de política
Endpoint	Roles
POST /laudos	analista
PUT /laudos/{id}	analista
POST /laudos/{id}/revisar	revisor
GET /laudos	visualizador
DELETE /laudos	admin
Headers obrigatórios

Authorization: Bearer

HTTPS obrigatório (via Nginx)

CORS restrito

ETAPA 8 — PREPARAÇÃO PARA MIGRAÇÃO FUTURA

Você já estará pronto porque:

✔ OIDC puro
✔ Claims padronizadas
✔ Backend não conhece Keycloak
✔ Config via env
✔ RBAC desacoplado

Trocar IdP = trocar:

URLs

Client config

Frontend adapter

CHECKLIST FINAL

Keycloak como IdP

JWT padronizado

Middleware genérico

Frontend com refresh

RBAC limpo

Migração futura simples

Próximo passo (sugestões)

Posso:

🧪 Criar testes automatizados de segurança

🔐 Sugerir MFA + políticas de senha

📦 Ajustar isso para microserviços

📊 Criar auditoria de ações (laudos)
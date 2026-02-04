# 🎯 PASSO 3 - QUICK START GUIDE

## 🚀 Iniciar o Projeto Completo

```bash
cd /opt/app/sistema_de_laudos

# Inicia todos os containers
docker compose up -d

# Verifica status
docker compose ps
```

## 🌐 Acessar Aplicação

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Login via Keycloak |
| **Backend API** | http://localhost:8000 | API REST |
| **Keycloak Admin** | http://localhost:8081/admin | kcadmin_dev / Dev@)((42)) |

## 👤 Teste Rápido - Login

1. Abra http://localhost:5173
2. Clique em "Entrar"
3. Use uma credencial:
   - **Admin**: admin@test.com / Password@123
   - **Analyst**: analyst@test.com / Password@123
   - **User**: user@test.com / Password@123

## 📝 Estrutura OIDC

```
Frontend (React)
    ↓
OIDCAuthProvider (src/contexts/AuthContext.jsx)
    ├── UserManager (oidc-client-ts)
    ├── Login/Logout handlers
    ├── Token management
    └── Role-based access

Keycloak
    ├── Realm: sistema_laudos_dev
    ├── Client: sistema_laudos_backend_dev
    ├── Roles: admin, analyst, user
    └── Users: 3 test users
```

## 🔑 Implementações Principais

### 1. AuthContext (Principal)
```javascript
// src/contexts/AuthContext.jsx
- Inicializa OIDC UserManager
- Gerencia sessão de usuário
- Fornece hooks para componentes
- Token refresh automático
```

### 2. Protected Routes
```javascript
// src/components/ProtectedRoute.jsx
- Verifica autenticação
- Valida roles (RBAC)
- Redireciona para login
```

### 3. Login Component
```javascript
// src/components/Login.jsx
- Botão de login/logout
- Exibe info do usuário
- Estilos responsivos
```

## 🔄 Fluxo de Token

```
1. Login → Redireciona para Keycloak
2. Keycloak Auth → Redireciona para /callback com code
3. Callback → Troca code por tokens (access + refresh)
4. Armazena → localStorage
5. Background refresh → 10s em 10s
6. Expired → Redireciona para login
```

## 📊 Componentes de Autenticação

| Arquivo | Responsabilidade |
|---------|-----------------|
| `AuthContext.jsx` | Gerenciamento OIDC principal |
| `Login.jsx` | UI de login/logout |
| `ProtectedRoute.jsx` | Proteção de rotas |
| `Callback.jsx` | Processamento de callback |
| `useAuth.js` | Hooks customizados |
| `Navbar.jsx` | Integração na navbar |

## 🧪 Teste de Roles

```bash
# Admin (role: admin)
admin@test.com / Password@123

# Analyst (role: analyst)  
analyst@test.com / Password@123

# User (role: user)
user@test.com / Password@123
```

## 🔧 Variáveis de Ambiente

`.env.dev` no frontend:
```
VITE_KEYCLOAK_URL=http://localhost:8081
VITE_KEYCLOAK_REALM=sistema_laudos_dev
VITE_KEYCLOAK_CLIENT_ID=sistema_laudos_backend_dev
VITE_KEYCLOAK_CLIENT_SECRET=frTqxpABgXCkikANferUADHYqlmrReYW
VITE_API_URL=http://localhost:8000/api
```

## 🚨 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Callback não funciona | Verificar `.env.dev` > URL de callback em Keycloak |
| Token não adicionado | Usar `useRequestInterceptor()` ou adicionar manualmente |
| CORS error | Verificar CORS no backend + Web Origins no Keycloak |
| Silent renew falha | Limpar cache, verificar `public/silent-renew.html` |

## 📚 Próximos Passos

**PASSO 4**: Testing & Validation (2-3 horas)
- [ ] 170+ testes backend
- [ ] E2E login testing
- [ ] Coverage 80%+

**PASSO 5**: Deployment (1-2 horas)
- [ ] HTTPS setup
- [ ] Production .env
- [ ] Docker production

---

**Status**: ✅ FRONTEND OIDC INTEGRATION COMPLETE

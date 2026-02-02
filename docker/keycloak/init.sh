#!/bin/bash
# ============================================
# Script de inicialização do Keycloak
# Cria Realm, Clients e Roles
# ============================================

set -e

# Variáveis
KEYCLOAK_URL=${KEYCLOAK_URL:-"http://localhost:8080"}
ADMIN_USER=${KEYCLOAK_ADMIN_USER:-"admin"}
ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD:-"keycloak_admin_123"}
REALM=${KEYCLOAK_REALM:-"sistema_laudos"}
BACKEND_CLIENT_ID=${KEYCLOAK_CLIENT_ID:-"sistema_laudos_backend"}
FRONTEND_CLIENT_ID="sistema_laudos_frontend"

echo "🔧 Configurando Keycloak..."
echo "Realm: $REALM"
echo "Backend Client: $BACKEND_CLIENT_ID"
echo "Frontend Client: $FRONTEND_CLIENT_ID"

# Aguardar Keycloak ficar pronto
echo "⏳ Aguardando Keycloak estar disponível..."
for i in {1..30}; do
    if curl -s "$KEYCLOAK_URL/health/ready" > /dev/null; then
        echo "✅ Keycloak está pronto"
        break
    fi
    echo "Tentativa $i/30..."
    sleep 2
done

# Obter token de admin
echo "🔐 Autenticando com admin..."
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "client_id=admin-cli" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASSWORD" \
    -d "grant_type=password" | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "❌ Erro ao obter token de admin"
    exit 1
fi

echo "✅ Token obtido com sucesso"

# ============================================
# Criar Realm
# ============================================
echo "📝 Criando Realm '$REALM'..."
curl -s -X POST "$KEYCLOAK_URL/admin/realms" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "realm": "'$REALM'",
        "enabled": true,
        "accessTokenLifespan": 1800,
        "refreshTokenMaxReuse": 0,
        "refreshTokenLifespan": 2592000,
        "offlineSessionIdleTimeout": 2592000,
        "sslRequired": "external",
        "publicClient": false,
        "protocolMappers": []
    }' || echo "⚠️ Realm talvez já exista"

# ============================================
# Criar Client Backend
# ============================================
echo "📝 Criando Client Backend..."
BACKEND_CLIENT_RESPONSE=$(curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "'$BACKEND_CLIENT_ID'",
        "name": "Backend API",
        "description": "FastAPI Backend for Sistema de Laudos",
        "enabled": true,
        "publicClient": false,
        "directAccessGrantsEnabled": true,
        "serviceAccountsEnabled": true,
        "standardFlowEnabled": true,
        "implicitFlowEnabled": false,
        "bearerOnlyClient": false,
        "consentRequired": false,
        "frontchannelLogoutSessionRequired": false,
        "validRedirectUris": [
            "http://localhost:8000/api/v1/auth/callback",
            "http://backend:8000/api/v1/auth/callback"
        ],
        "webOrigins": [
            "http://localhost:8000",
            "http://backend:8000"
        ],
        "redirectUris": [
            "http://localhost:8000/api/v1/auth/callback",
            "http://backend:8000/api/v1/auth/callback"
        ]
    }')

BACKEND_CLIENT_UUID=$(echo "$BACKEND_CLIENT_RESPONSE" | jq -r '.id')
echo "✅ Cliente Backend criado: $BACKEND_CLIENT_UUID"

# ============================================
# Criar Client Frontend
# ============================================
echo "📝 Criando Client Frontend..."
FRONTEND_CLIENT_RESPONSE=$(curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "'$FRONTEND_CLIENT_ID'",
        "name": "Frontend Web",
        "description": "React Frontend for Sistema de Laudos",
        "enabled": true,
        "publicClient": true,
        "directAccessGrantsEnabled": true,
        "standardFlowEnabled": true,
        "implicitFlowEnabled": true,
        "serviceAccountsEnabled": false,
        "consentRequired": false,
        "frontchannelLogoutSessionRequired": false,
        "validRedirectUris": [
            "http://localhost:5173/*",
            "http://localhost/*",
            "http://frontend/*"
        ],
        "webOrigins": [
            "http://localhost:5173",
            "http://localhost",
            "http://frontend"
        ],
        "redirectUris": [
            "http://localhost:5173/*",
            "http://localhost/*"
        ]
    }')

FRONTEND_CLIENT_UUID=$(echo "$FRONTEND_CLIENT_RESPONSE" | jq -r '.id')
echo "✅ Cliente Frontend criado: $FRONTEND_CLIENT_UUID"

# ============================================
# Criar Roles
# ============================================
echo "📝 Criando Roles..."

ROLES=("admin" "analyst" "viewer" "supervisor")

for role in "${ROLES[@]}"; do
    curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM/roles" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "'$role'",
            "description": "Permissão de '"$role"'",
            "composite": false,
            "clientRole": false
        }' || echo "⚠️ Role '$role' talvez já exista"
done

echo "✅ Roles criados com sucesso"

# ============================================
# Criar Usuário Demo
# ============================================
echo "📝 Criando usuário de demonstração..."
DEMO_USER_RESPONSE=$(curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM/users" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "demo",
        "email": "demo@example.com",
        "firstName": "Usuário",
        "lastName": "Demo",
        "enabled": true,
        "emailVerified": false,
        "credentials": [{
            "type": "password",
            "value": "demo123456",
            "temporary": false
        }]
    }')

DEMO_USER_ID=$(echo "$DEMO_USER_RESPONSE" | jq -r '.id')
echo "✅ Usuário demo criado: $DEMO_USER_ID"

# ============================================
# Atribuir Roles ao Usuário Demo
# ============================================
echo "📝 Atribuindo roles ao usuário demo..."
curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM/users/$DEMO_USER_ID/role-mappings/realm" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '[
        {"name": "admin"},
        {"name": "analyst"}
    ]' || echo "⚠️ Erro ao atribuir roles"

echo "✅ Roles atribuidos com sucesso"

# ============================================
# Obter Secret do Cliente Backend
# ============================================
echo "🔐 Obtendo secret do cliente backend..."
BACKEND_SECRET=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients/$BACKEND_CLIENT_UUID/client-secret" \
    -H "Authorization: Bearer $TOKEN" | jq -r '.value')

echo "✅ Configuração do Keycloak concluída com sucesso!"
echo ""
echo "📋 Informações de Configuração:"
echo "================================"
echo "Realm: $REALM"
echo "Backend Client ID: $BACKEND_CLIENT_ID"
echo "Backend Client Secret: $BACKEND_SECRET"
echo "Frontend Client ID: $FRONTEND_CLIENT_ID"
echo "URL Keycloak: $KEYCLOAK_URL"
echo ""
echo "Usuário Demo:"
echo "  Username: demo"
echo "  Password: demo123456"
echo ""
echo "👉 Atualize o arquivo .env com as credenciais acima"

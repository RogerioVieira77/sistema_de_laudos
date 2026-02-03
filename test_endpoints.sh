#!/bin/bash

# ============================================
# Script de Testes - Sistema de Laudos
# Data: 02/02/2026
# ============================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variáveis
BASE_URL="http://localhost"
BACKEND_URL="http://localhost:8000"
API_URL="$BASE_URL/api/v1"
TEST_USER_ID="1"
TEST_TOKEN="test-token-123"

# Contadores
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local expected_code=$4
    local data=$5
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Test #$TOTAL_TESTS: $description${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "Method: ${YELLOW}$method${NC}"
    echo -e "Endpoint: ${YELLOW}$endpoint${NC}"
    echo -e "Expected Status: ${YELLOW}$expected_code${NC}"
    
    # Executar request
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TEST_TOKEN" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Authorization: Bearer $TEST_TOKEN")
    fi
    
    # Separar response body e status code
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    echo -e "Actual Status: ${YELLOW}$http_code${NC}"
    
    # Verificar se passou no teste
    if [ "$http_code" == "$expected_code" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Mostrar resposta se não estiver vazia
        if [ -n "$body" ] && [ "$body" != "" ]; then
            echo -e "\nResponse:"
            echo "$body" | head -c 500
            if [ ${#body} -gt 500 ]; then
                echo "... (truncated)"
            fi
        fi
    else
        echo -e "${RED}✗ FAILED (Expected $expected_code, got $http_code)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo -e "\nResponse:"
        echo "$body"
    fi
}

# ============================================
# TESTES - HEALTH CHECK
# ============================================

echo -e "\n${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          TESTES - HEALTH CHECK                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"

test_endpoint "GET" "/health" "Health check do backend" "200"

# ============================================
# TESTES - CONTRATOS
# ============================================

echo -e "\n\n${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       TESTES - ENDPOINTS DE CONTRATOS          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"

test_endpoint "GET" "/contratos" "Listar contratos (vazio)" "200"

# ============================================
# TESTES - BUREAU
# ============================================

echo -e "\n\n${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        TESTES - ENDPOINTS DE BUREAU            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"

test_endpoint "GET" "/bureau" "Listar registros de bureau" "200"

# ============================================
# TESTES - PARECERES
# ============================================

echo -e "\n\n${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       TESTES - ENDPOINTS DE PARECERES          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"

test_endpoint "GET" "/pareceres" "Listar pareceres" "200"

test_endpoint "GET" "/pareceres/estatisticas/resumo" "Obter estatísticas de pareceres" "200"

# ============================================
# TESTES - GEOLOCALIZAÇÃO
# ============================================

echo -e "\n\n${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    TESTES - ENDPOINTS DE GEOLOCALIZAÇÃO        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"

test_endpoint "GET" "/geolocalizacao/1" "Buscar análise de geolocalização (inexistente)" "404"

# ============================================
# TESTES - 404
# ============================================

echo -e "\n\n${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           TESTES - VALIDAÇÃO 404               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"

test_endpoint "GET" "/contratos/999" "Buscar contrato inexistente" "404"

test_endpoint "GET" "/pareceres/999" "Buscar parecer inexistente" "404"

# ============================================
# SWAGGER/REDOC
# ============================================

echo -e "\n\n${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    TESTES - DOCUMENTAÇÃO (SWAGGER/REDOC)       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"

# Testar Swagger
swagger_response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/docs")
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test #$((TOTAL_TESTS + 1)): Swagger UI${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Endpoint: ${YELLOW}$BACKEND_URL/api/v1/docs${NC}"
echo -e "Status: ${YELLOW}$swagger_response${NC}"

if [ "$swagger_response" == "200" ]; then
    echo -e "${GREEN}✓ Swagger UI acessível${NC}"
else
    echo -e "${RED}✗ Swagger UI não acessível${NC}"
fi

# Testar ReDoc
redoc_response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/redoc")
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test #$((TOTAL_TESTS + 2)): ReDoc${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Endpoint: ${YELLOW}$BACKEND_URL/api/v1/redoc${NC}"
echo -e "Status: ${YELLOW}$redoc_response${NC}"

if [ "$redoc_response" == "200" ]; then
    echo -e "${GREEN}✓ ReDoc acessível${NC}"
else
    echo -e "${RED}✗ ReDoc não acessível${NC}"
fi

# ============================================
# RESUMO FINAL
# ============================================

echo -e "\n\n${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            RESUMO DOS TESTES                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"

echo -e "\nTotal de testes: ${YELLOW}$TOTAL_TESTS${NC}"
echo -e "Testes passou: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Testes falharam: ${RED}$FAILED_TESTS${NC}"

# Calcular taxa de sucesso
if [ $TOTAL_TESTS -gt 0 ]; then
    success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "Taxa de sucesso: ${YELLOW}$success_rate%${NC}"
fi

# Status final
echo ""
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ TODOS OS TESTES PASSARAM!${NC}"
    exit 0
else
    echo -e "${RED}✗ ALGUNS TESTES FALHARAM${NC}"
    exit 1
fi

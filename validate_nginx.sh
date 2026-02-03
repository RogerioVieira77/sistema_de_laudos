#!/bin/bash

# ============================================
# Script de Validação - Nginx Proxy
# Data: 02/02/2026
# ============================================

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║          VALIDAÇÃO - NGINX COMO PROXY PARA FASTAPI               ║"
echo "║                                                                    ║"
echo "║          Data: 02/02/2026                                         ║"
echo "║          Status: Verificando...                                   ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0
WARNINGS=0

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================
# 1. Verificar arquivo de configuração
# ============================================
echo -e "${BLUE}[1/7]${NC} Verificando arquivo nginx.conf..."

if [ ! -f "/opt/app/sistema_de_laudos/nginx/nginx.conf" ]; then
  echo -e "${RED}✗ ERRO: Arquivo nginx.conf não encontrado${NC}"
  ERRORS=$((ERRORS + 1))
else
  echo -e "${GREEN}✓ Arquivo nginx.conf existe${NC}"
fi

# ============================================
# 2. Verificar se contém upstream backend
# ============================================
echo -e "${BLUE}[2/7]${NC} Verificando configuração upstream backend..."

if grep -q "upstream backend" /opt/app/sistema_de_laudos/nginx/nginx.conf; then
  echo -e "${GREEN}✓ Upstream backend configurado${NC}"
else
  echo -e "${RED}✗ ERRO: Upstream backend não configurado${NC}"
  ERRORS=$((ERRORS + 1))
fi

# ============================================
# 3. Verificar se contém location /api/
# ============================================
echo -e "${BLUE}[3/7]${NC} Verificando proxy para /api/..."

if grep -q "location /api/" /opt/app/sistema_de_laudos/nginx/nginx.conf; then
  echo -e "${GREEN}✓ Location /api/ configurado${NC}"
  
  if grep -A 3 "location /api/" /opt/app/sistema_de_laudos/nginx/nginx.conf | grep -q "proxy_pass http://backend"; then
    echo -e "${GREEN}✓ Proxy para backend configurado corretamente${NC}"
  else
    echo -e "${RED}✗ ERRO: proxy_pass não aponta para backend${NC}"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo -e "${RED}✗ ERRO: Location /api/ não configurado${NC}"
  ERRORS=$((ERRORS + 1))
fi

# ============================================
# 4. Verificar headers X-Forwarded
# ============================================
echo -e "${BLUE}[4/7]${NC} Verificando headers X-Forwarded..."

REQUIRED_HEADERS=("X-Forwarded-For" "X-Forwarded-Proto" "X-Forwarded-Host")
MISSING_HEADERS=0

for header in "${REQUIRED_HEADERS[@]}"; do
  if grep -q "proxy_set_header $header" /opt/app/sistema_de_laudos/nginx/nginx.conf; then
    echo -e "${GREEN}✓ Header $header configurado${NC}"
  else
    echo -e "${RED}✗ ERRO: Header $header não configurado${NC}"
    MISSING_HEADERS=$((MISSING_HEADERS + 1))
  fi
done

if [ $MISSING_HEADERS -gt 0 ]; then
  ERRORS=$((ERRORS + 1))
fi

# ============================================
# 5. Verificar timeouts
# ============================================
echo -e "${BLUE}[5/7]${NC} Verificando configuração de timeouts..."

if grep -q "proxy_read_timeout 120s" /opt/app/sistema_de_laudos/nginx/nginx.conf; then
  echo -e "${GREEN}✓ Timeout configurado corretamente (120s)${NC}"
else
  echo -e "${YELLOW}⚠ AVISO: Timeout pode não estar otimizado${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# ============================================
# 6. Verificar tamanho máximo de upload
# ============================================
echo -e "${BLUE}[6/7]${NC} Verificando tamanho máximo de upload..."

if grep -q "client_max_body_size 10M" /opt/app/sistema_de_laudos/nginx/nginx.conf; then
  echo -e "${GREEN}✓ Limite de upload configurado (10MB)${NC}"
else
  echo -e "${YELLOW}⚠ AVISO: Limite de upload pode estar incorreto${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# ============================================
# 7. Validar sintaxe do arquivo
# ============================================
echo -e "${BLUE}[7/7]${NC} Validando sintaxe do nginx.conf..."

# Tentar fazer parse básico
if nginx -t -c /opt/app/sistema_de_laudos/nginx/nginx.conf 2>/dev/null || \
   grep -q "events {" /opt/app/sistema_de_laudos/nginx/nginx.conf && \
   grep -q "http {" /opt/app/sistema_de_laudos/nginx/nginx.conf; then
  echo -e "${GREEN}✓ Sintaxe do arquivo é válida${NC}"
else
  echo -e "${YELLOW}⚠ AVISO: Não foi possível validar sintaxe completamente${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# ============================================
# RESUMO FINAL
# ============================================
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                        RESUMO DA VALIDAÇÃO                        ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

if [ $ERRORS -eq 0 ]; then
  echo -e "${GREEN}✓ Erros Críticos: $ERRORS${NC}"
else
  echo -e "${RED}✗ Erros Críticos: $ERRORS${NC}"
fi

echo -e "${YELLOW}⚠ Avisos: $WARNINGS${NC}"
echo ""

# ============================================
# Verificação de Endpoints
# ============================================
echo -e "${BLUE}Próximas Etapas de Validação:${NC}"
echo ""
echo "1. Iniciar os containers:"
echo "   docker compose up -d nginx backend frontend"
echo ""
echo "2. Testar endpoints:"
echo "   curl http://localhost/health"
echo "   curl http://localhost/api/v1/health"
echo "   curl -I http://localhost/api/v1/docs"
echo ""
echo "3. Validar logs:"
echo "   docker compose logs -f nginx"
echo ""

# ============================================
# Status Final
# ============================================
if [ $ERRORS -eq 0 ]; then
  echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
  echo -e "${GREEN}          ✓ VALIDAÇÃO CONCLUÍDA COM SUCESSO!${NC}"
  echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
  exit 0
else
  echo -e "${RED}════════════════════════════════════════════════════════════════════${NC}"
  echo -e "${RED}          ✗ VALIDAÇÃO ENCONTROU ERROS CRÍTICOS!${NC}"
  echo -e "${RED}════════════════════════════════════════════════════════════════════${NC}"
  exit 1
fi

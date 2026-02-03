# GUIA DE TESTE - FASE 4.4 API ENDPOINTS

**Data:** 02/02/2026  
**Versão:** 1.0.0  
**Status:** Pronto para Testes

---

## 🚀 Como Iniciar o Servidor

### Opção 1: Com Docker Compose (Recomendado)

```bash
cd /opt/app/sistema_de_laudos

# Validar configuração
docker compose config

# Compilar imagens
docker compose build backend

# Iniciar serviço
docker compose up -d backend postgres

# Verificar logs
docker compose logs -f backend
```

### Opção 2: Desenvolvimento Local

```bash
cd /opt/app/sistema_de_laudos/backend

# Instalar dependências
pip install -r requirements.txt

# Executar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📍 URLs da API

| Recurso | URL |
|---------|-----|
| API | `http://82.25.75.88:8000/` |
| Health | `http://82.25.75.88:8000/api/v1/health` |
| Swagger Docs | `http://82.25.75.88:8000/docs` |
| ReDoc | `http://82.25.75.88:8000/redoc` |
| OpenAPI JSON | `http://82.25.75.88:8000/openapi.json` |

---

## ✅ TESTE 1: Health Check (Público - Sem Autenticação)

```bash
curl -X GET http://82.25.75.88:8000/api/v1/health

# Response esperada (200 OK):
{
  "status": "OK",
  "timestamp": "2024-02-02T10:50:00.123456Z",
  "service": "Sistema de Laudos Backend",
  "version": "1.0.0",
  "components": {
    "api": "UP",
    "database": "UP"
  }
}
```

---

## ✅ TESTE 2: Contratos - Listar (Com Autenticação)

### Request
```bash
curl -X GET "http://82.25.75.88:8000/api/v1/contratos?skip=0&limit=10" \
  -H "Authorization: Bearer 1"

# Ou com curl simples:
curl http://82.25.75.88:8000/api/v1/contratos -H "Authorization: Bearer 1"
```

### Response esperada (200 OK)
```json
{
  "total": 0,
  "skip": 0,
  "limit": 10,
  "contratos": []
}
```

---

## ✅ TESTE 3: Contratos - Upload de PDF

### Pré-requisito
Criar um arquivo PDF de teste:
```bash
# Criar PDF simples com Python
python3 << 'EOF'
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("/tmp/test_contract.pdf", pagesize=letter)
c.drawString(100, 750, "Contrato de Teste")
c.drawString(100, 730, "CPF: 12345678901")
c.drawString(100, 710, "Numero: CTR-001")
c.save()
print("✅ PDF criado: /tmp/test_contract.pdf")
EOF
```

### Request
```bash
curl -X POST "http://82.25.75.88:8000/api/v1/contratos/upload?numero_contrato=CTR-001&cpf_cliente=12345678901" \
  -H "Authorization: Bearer 1" \
  -F "file=@/tmp/test_contract.pdf"
```

### Response esperada (201 Created)
```json
{
  "id": 1,
  "usuario_id": 1,
  "numero_contrato": "CTR-001",
  "cpf_cliente": "12345678901",
  "latitude": null,
  "longitude": null,
  "endereco_assinatura": "Extraído do PDF",
  "status": "RECEBIDO",
  "arquivo_pdf_path": "/uploads/contratos/1_CTR-001.pdf",
  "criado_em": "2024-02-02T10:30:00Z",
  "atualizado_em": "2024-02-02T10:30:00Z"
}
```

---

## ✅ TESTE 4: Contratos - Buscar Específico

```bash
curl -X GET http://82.25.75.88:8000/api/v1/contratos/1 \
  -H "Authorization: Bearer 1"

# Response esperada (200 OK):
# Mesmo JSON do upload
```

---

## ✅ TESTE 5: Bureau - Listar

```bash
curl -X GET http://82.25.75.88:8000/api/v1/bureau \
  -H "Authorization: Bearer 1"

# Response esperada (200 OK):
{
  "total": 0,
  "skip": 0,
  "limit": 10,
  "items": []
}
```

---

## ✅ TESTE 6: Bureau - Buscar Específico

```bash
curl -X GET http://82.25.75.88:8000/api/v1/bureau/1 \
  -H "Authorization: Bearer 1"

# Response esperada (404 Not Found):
{
  "detail": "Dados de Bureau não encontrados para contrato ID: 1"
}
```

---

## ✅ TESTE 7: Geolocalização - Analisar

```bash
curl -X POST http://82.25.75.88:8000/api/v1/geolocalizacao/analisar \
  -H "Authorization: Bearer 1" \
  -H "Content-Type: application/json" \
  -d '{
    "contrato_id": 1,
    "forcar_atualizacao": false
  }'

# Response esperada (422 Unprocessable Entity):
# Dados insuficientes (bureau não existe ou sem coordenadas)
```

---

## ✅ TESTE 8: Pareceres - Listar

```bash
curl -X GET http://82.25.75.88:8000/api/v1/pareceres \
  -H "Authorization: Bearer 1"

# Response esperada (200 OK):
{
  "total": 0,
  "skip": 0,
  "limit": 10,
  "items": []
}
```

---

## ✅ TESTE 9: Pareceres - Estatísticas

```bash
curl -X GET http://82.25.75.88:8000/api/v1/pareceres/estatisticas/resumo \
  -H "Authorization: Bearer 1"

# Response esperada (200 OK):
{
  "total_pareceres": 0,
  "por_tipo": {
    "PROXIMAL": 0,
    "MODERADO": 0,
    "DISTANTE": 0,
    "MUITO_DISTANTE": 0
  },
  "distancia_media_km": 0,
  "distancia_minima_km": 0,
  "distancia_maxima_km": 0
}
```

---

## ✅ TESTE 10: Testes de Erro - Sem Autenticação

```bash
curl -X GET http://82.25.75.88:8000/api/v1/contratos

# Response esperada (401 Unauthorized):
{
  "detail": "Token não fornecido"
}
```

---

## ✅ TESTE 11: Testes de Erro - Recurso Não Encontrado

```bash
curl -X GET http://82.25.75.88:8000/api/v1/contratos/999 \
  -H "Authorization: Bearer 1"

# Response esperada (404 Not Found):
{
  "detail": "Contrato não encontrado (ID: 999)"
}
```

---

## ✅ TESTE 12: Testes de Erro - Permissão Negada

```bash
curl -X DELETE http://82.25.75.88:8000/api/v1/contratos/1 \
  -H "Authorization: Bearer 2"  # Usuário diferente

# Response esperada (403 Forbidden):
{
  "detail": "Sem permissão: Você não tem permissão para deletar este contrato"
}
```

---

## 🧪 Testes com Postman

1. **Importar Collection**
   ```
   File → Import → Paste Raw Text
   ```

2. **Collection JSON** (salvar como `Sistema-Laudos.postman_collection.json`)
   ```json
   {
     "info": {
       "name": "Sistema de Laudos API",
       "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
     },
     "item": [
       {
         "name": "Health Check",
         "request": {
           "method": "GET",
           "url": "http://82.25.75.88:8000/api/v1/health"
         }
       },
       {
         "name": "List Contratos",
         "request": {
           "method": "GET",
           "header": [
             {
               "key": "Authorization",
               "value": "Bearer 1"
             }
           ],
           "url": "http://82.25.75.88:8000/api/v1/contratos"
         }
       }
     ]
   }
   ```

---

## 📊 Checklist de Testes

### Endpoints Obrigatórios

- [ ] Health Check (GET /health) - Público
- [ ] Listar Contratos (GET /contratos) - Autenticado
- [ ] Upload Contrato (POST /contratos/upload) - Autenticado
- [ ] Buscar Contrato (GET /contratos/{id}) - Autenticado
- [ ] Deletar Contrato (DELETE /contratos/{id}) - Autenticado
- [ ] Listar Bureau (GET /bureau) - Autenticado
- [ ] Buscar Bureau (GET /bureau/{id}) - Autenticado
- [ ] Analisar Geo (POST /geolocalizacao/analisar) - Autenticado
- [ ] Listar Pareceres (GET /pareceres) - Autenticado
- [ ] Buscar Parecer (GET /pareceres/{id}) - Autenticado
- [ ] Estatísticas (GET /pareceres/estatisticas/resumo) - Autenticado
- [ ] Deletar Parecer (DELETE /pareceres/{id}) - Autenticado

### Validações de Erro

- [ ] 401 Unauthorized - Sem token
- [ ] 403 Forbidden - Sem permissão
- [ ] 404 Not Found - Recurso inexistente
- [ ] 400 Bad Request - Arquivo inválido
- [ ] 413 Payload Too Large - Arquivo muito grande
- [ ] 422 Unprocessable Entity - Dados inválidos

### Documentação

- [ ] Swagger UI funciona (/docs)
- [ ] ReDoc funciona (/redoc)
- [ ] Todos endpoints documentados
- [ ] Schemas Pydantic aparecem
- [ ] Exemplos de erro aparecem

---

## 🐛 Troubleshooting

### Erro: ModuleNotFoundError
```
Solution: Instalar dependências
pip install -r requirements.txt
```

### Erro: Connection refused
```
Solution: Verificar se servidor está rodando
docker ps
curl http://82.25.75.88:8000/api/v1/health
```

### Erro: Database not available
```
Solution: Garantir que Postgres está rodando
docker compose ps postgres
docker compose logs postgres
```

### Erro: CORS issue
```
Solution: CORS já está configurado em main.py
Se precisar, ajustar allow_origins em CORSMiddleware
```

---

## 📝 Registrar Resultados

Ao completar os testes, documentar:

1. **Data/Hora do Teste**
2. **Versão da API**
3. **Endpoints Testados**
4. **Bugs Encontrados** (se houver)
5. **Melhorias Sugeridas**
6. **Status Final** (✅ PASSOU / ⚠️ FALHOU)

---

## 🎯 Próximas Etapas

Após conclusão dos testes:

1. Corrigir bugs encontrados
2. Validar documentação Swagger
3. Proceder para Phase 5 (Frontend)
4. Integração entre Frontend e Backend

---

**Teste elaborado por:** Backend Team  
**Data:** 02/02/2026  
**Status:** Pronto para Execução

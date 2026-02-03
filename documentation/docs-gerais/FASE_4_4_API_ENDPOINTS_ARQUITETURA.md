# FASE 4.4 - API Endpoints (Arquitetura Detalhada)

**Data:** 02/02/2026  
**Versão:** 1.0.0  
**Responsável:** Backend Team  
**Duração Estimada:** 2-3 dias

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Arquitetura de Routers](#arquitetura-de-routers)
3. [Endpoints Detalhados](#endpoints-detalhados)
4. [Fluxos de Dados](#fluxos-de-dados)
5. [Tratamento de Erros](#tratamento-de-erros)
6. [Segurança](#segurança)

---

## 🎯 Visão Geral

### Propósito
Expor a lógica de negócio desenvolvida na Phase 4.3 através de endpoints HTTP REST utilizando FastAPI.

### Componentes Principais

```
┌─────────────────────────────────────────────────┐
│         FastAPI Application (main.py)           │
├─────────────────────────────────────────────────┤
│  Router Principal (include_router)              │
│  ├── /api/v1/contratos (contratos.py)          │
│  ├── /api/v1/bureau (bureau.py)                │
│  ├── /api/v1/geolocalizacao (geolocalizacao.py)│
│  ├── /api/v1/pareceres (pareceres.py)          │
│  └── /api/v1/health (health check)             │
├─────────────────────────────────────────────────┤
│         Services Layer (já implementado)        │
│  ├── ContratoService                           │
│  ├── BureauService                             │
│  ├── GeolocalizacaoService                     │
│  └── PareceService                             │
├─────────────────────────────────────────────────┤
│      Repositories Layer (já implementado)       │
│  ├── ContratoRepository                        │
│  ├── BureauRepository                          │
│  └── PareceRepository                          │
└─────────────────────────────────────────────────┘
```

---

## 🏗️ Arquitetura de Routers

### Estrutura de Pastas

```
backend/app/
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py          ← Registra routers
│   │   ├── contratos.py         ← Router de contratos
│   │   ├── bureau.py            ← Router de bureau
│   │   ├── geolocalizacao.py    ← Router de geolocalização
│   │   ├── pareceres.py         ← Router de pareceres
│   │   └── health.py            ← Router de health check
│   └── dependencies.py          ← Injeção de dependências
├── main.py                      ← Modificar para incluir routers
```

### Padrão de Router

```python
# Exemplo: backend/app/api/v1/contratos.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.schemas import ContratoCreate, ContratoResponse, ContratoListResponse
from app.services import ContratoService
from app.api.dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/v1/contratos",
    tags=["Contratos"],
    responses={404: {"description": "Not found"}}
)

# Dependency injection
def get_contrato_service(db: Session = Depends(get_db)) -> ContratoService:
    return ContratoService(db)

@router.post(
    "/upload",
    response_model=ContratoResponse,
    status_code=201,
    summary="Upload de Contrato",
    description="Faz upload de um PDF de contrato e extrai dados"
)
async def upload_contrato(
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user),
    service: ContratoService = Depends(get_contrato_service)
):
    """
    ### Fluxo:
    1. Validar arquivo PDF
    2. Extrair dados (CPF, número, coordenadas)
    3. Salvar em dados_contrato
    4. Retornar ID para referência
    """
    pass

@router.get(
    "/{contrato_id}",
    response_model=ContratoResponse,
    summary="Obter Contrato",
    description="Busca um contrato específico pelo ID"
)
async def get_contrato(
    contrato_id: int,
    current_user_id: int = Depends(get_current_user),
    service: ContratoService = Depends(get_contrato_service)
):
    pass

@router.get(
    "",
    response_model=ContratoListResponse,
    summary="Listar Contratos",
    description="Lista todos os contratos do usuário com paginação"
)
async def list_contratos(
    skip: int = 0,
    limit: int = 10,
    current_user_id: int = Depends(get_current_user),
    service: ContratoService = Depends(get_contrato_service)
):
    pass

@router.delete(
    "/{contrato_id}",
    status_code=204,
    summary="Deletar Contrato",
    description="Deleta um contrato"
)
async def delete_contrato(
    contrato_id: int,
    current_user_id: int = Depends(get_current_user),
    service: ContratoService = Depends(get_contrato_service)
):
    pass
```

---

## 🔌 Endpoints Detalhados

### 1. Router: Contratos (`/api/v1/contratos`)

#### 1.1 POST /api/v1/contratos/upload
```yaml
Nome: Upload de Contrato
Autenticação: Obrigatória (JWT)
Content-Type: multipart/form-data

Request:
  - file: UploadFile (PDF obrigatório)

Response (201 Created):
  {
    "id": 1,
    "usuario_id": 1,
    "numero_contrato": "CTR-2024-001",
    "cpf_cliente": "123.456.789-00",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "endereco_assinatura": "Rua X, 100, São Paulo",
    "status": "PROCESSANDO",
    "criado_em": "2024-02-02T10:30:00Z",
    "atualizado_em": "2024-02-02T10:30:00Z"
  }

Errors:
  400: Arquivo inválido
  413: Arquivo muito grande (> 10MB)
  500: Erro ao extrair PDF
```

**Fluxo Interno:**
1. Validar arquivo (tipo, tamanho)
2. Salvar arquivo temporariamente
3. Extrair dados com `PDFExtractor`
4. Chamar `ContratoService.criar_contrato()`
5. Retornar objeto criado

---

#### 1.2 GET /api/v1/contratos/{contrato_id}
```yaml
Nome: Obter Contrato
Autenticação: Obrigatória
Parâmetros:
  - contrato_id: int (path)

Response (200 OK):
  {
    "id": 1,
    "usuario_id": 1,
    "numero_contrato": "CTR-2024-001",
    "cpf_cliente": "123.456.789-00",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "endereco_assinatura": "Rua X, 100, São Paulo",
    "status": "CONCLUÍDO",
    "arquivo_pdf_path": "/uploads/contrato_1.pdf",
    "criado_em": "2024-02-02T10:30:00Z",
    "atualizado_em": "2024-02-02T10:45:00Z"
  }

Errors:
  404: Contrato não encontrado
  403: Sem permissão
```

---

#### 1.3 GET /api/v1/contratos
```yaml
Nome: Listar Contratos
Autenticação: Obrigatória
Query Parâmetros:
  - skip: int = 0
  - limit: int = 10
  - status: str (opcional) = TODOS

Response (200 OK):
  {
    "total": 25,
    "skip": 0,
    "limit": 10,
    "items": [
      { ...contrato... },
      { ...contrato... }
    ]
  }
```

---

#### 1.4 DELETE /api/v1/contratos/{contrato_id}
```yaml
Nome: Deletar Contrato
Autenticação: Obrigatória
Parâmetros:
  - contrato_id: int (path)

Response (204 No Content)

Errors:
  404: Contrato não encontrado
  403: Sem permissão
```

---

### 2. Router: Bureau (`/api/v1/bureau`)

#### 2.1 GET /api/v1/bureau/{contrato_id}
```yaml
Nome: Obter Dados de Bureau
Autenticação: Obrigatória
Parâmetros:
  - contrato_id: int (path)

Response (200 OK):
  {
    "id": 1,
    "contrato_id": 1,
    "cpf_cliente": "123.456.789-00",
    "nome_cliente": "João Silva",
    "logradouro": "Avenida Y, 200, São Paulo",
    "cep": "01310-100",
    "telefone": "(11) 9999-9999",
    "latitude": -23.5510,
    "longitude": -46.6340,
    "data_consulta": "2024-02-02T10:35:00Z",
    "criado_em": "2024-02-02T10:35:00Z"
  }

Errors:
  404: Dados de bureau não encontrados
  403: Sem permissão
```

---

#### 2.2 GET /api/v1/bureau
```yaml
Nome: Listar Todos os Bureau
Autenticação: Obrigatória
Query Parâmetros:
  - skip: int = 0
  - limit: int = 10
  - cpf: str (opcional)

Response (200 OK):
  {
    "total": 100,
    "skip": 0,
    "limit": 10,
    "items": [ ...bureaus... ]
  }
```

---

### 3. Router: Geolocalização (`/api/v1/geolocalizacao`)

#### 3.1 POST /api/v1/geolocalizacao/analisar
```yaml
Nome: Analisar Geolocalização
Autenticação: Obrigatória
Content-Type: application/json

Request:
  {
    "contrato_id": 1,
    "forcar_atualizacao": false
  }

Response (200 OK):
  {
    "contrato_id": 1,
    "endereco_origem": "Rua X, 100, São Paulo",
    "endereco_destino": "Avenida Y, 200, São Paulo",
    "latitude_origem": -23.5505,
    "longitude_origem": -46.6333,
    "latitude_destino": -23.5510,
    "longitude_destino": -46.6340,
    "distancia_km": 0.85,
    "tipo_parecer": "PROXIMAL",
    "texto_parecer": "Endereços estão muito próximos (< 5km)",
    "rota": [
      [-23.5505, -46.6333],
      [-23.5510, -46.6340]
    ],
    "confianca": 0.95,
    "timestamp": "2024-02-02T10:40:00Z"
  }

Errors:
  404: Contrato ou Bureau não encontrado
  422: Dados insuficientes para análise
  503: Serviço de geocodificação indisponível
```

**Fluxo Interno:**
1. Buscar dados_contrato
2. Buscar dados_bureau
3. Chamar `GeolocalizacaoService.analisar()`
4. Calcular distância (Haversine)
5. Gerar parecer baseado em regras
6. Salvar em pareceres
7. Retornar análise

---

#### 3.2 GET /api/v1/geolocalizacao/{contrato_id}
```yaml
Nome: Obter Análise de Geolocalização
Autenticação: Obrigatória
Parâmetros:
  - contrato_id: int (path)

Response (200 OK):
  {
    "contrato_id": 1,
    "distancia_km": 0.85,
    "tipo_parecer": "PROXIMAL",
    "ultima_atualizacao": "2024-02-02T10:40:00Z"
  }

Errors:
  404: Análise não encontrada
  403: Sem permissão
```

---

### 4. Router: Pareceres (`/api/v1/pareceres`)

#### 4.1 GET /api/v1/pareceres
```yaml
Nome: Listar Pareceres
Autenticação: Obrigatória
Query Parâmetros:
  - skip: int = 0
  - limit: int = 10
  - tipo_parecer: str (opcional) = TODOS|PROXIMAL|MODERADO|DISTANTE|MUITO_DISTANTE
  - data_inicio: datetime (opcional)
  - data_fim: datetime (opcional)
  - ordenar_por: str = data (data|distancia|tipo)

Response (200 OK):
  {
    "total": 50,
    "skip": 0,
    "limit": 10,
    "items": [
      {
        "id": 1,
        "contrato_id": 1,
        "distancia_km": 0.85,
        "tipo_parecer": "PROXIMAL",
        "texto_parecer": "Endereços estão muito próximos (< 5km)",
        "criado_em": "2024-02-02T10:40:00Z"
      }
    ]
  }
```

---

#### 4.2 GET /api/v1/pareceres/{parecer_id}
```yaml
Nome: Obter Parecer Específico
Autenticação: Obrigatória
Parâmetros:
  - parecer_id: int (path)

Response (200 OK):
  {
    "id": 1,
    "contrato_id": 1,
    "distancia_km": 0.85,
    "tipo_parecer": "PROXIMAL",
    "texto_parecer": "Endereços estão muito próximos (< 5km)",
    "latitude_inicio": -23.5505,
    "longitude_inicio": -46.6333,
    "latitude_fim": -23.5510,
    "longitude_fim": -46.6340,
    "criado_em": "2024-02-02T10:40:00Z"
  }

Errors:
  404: Parecer não encontrado
  403: Sem permissão
```

---

#### 4.3 GET /api/v1/pareceres/estatisticas
```yaml
Nome: Obter Estatísticas de Pareceres
Autenticação: Obrigatória

Response (200 OK):
  {
    "total_pareceres": 50,
    "por_tipo": {
      "PROXIMAL": 20,
      "MODERADO": 15,
      "DISTANTE": 10,
      "MUITO_DISTANTE": 5
    },
    "distancia_media_km": 45.3,
    "distancia_minima_km": 0.5,
    "distancia_maxima_km": 250.8
  }
```

---

#### 4.4 DELETE /api/v1/pareceres/{parecer_id}
```yaml
Nome: Deletar Parecer
Autenticação: Obrigatória
Parâmetros:
  - parecer_id: int (path)

Response (204 No Content)

Errors:
  404: Parecer não encontrado
  403: Sem permissão
```

---

### 5. Router: Health Check (`/api/v1/health`)

#### 5.1 GET /api/v1/health
```yaml
Nome: Health Check
Autenticação: Não obrigatória (pública)

Response (200 OK):
  {
    "status": "OK",
    "timestamp": "2024-02-02T10:50:00Z",
    "database": "CONNECTED",
    "redis": "CONNECTED",
    "version": "1.0.0"
  }
```

---

## 📊 Fluxos de Dados

### Fluxo 1: Upload e Análise Completa

```
1. Cliente faz POST /contratos/upload
   ↓
2. Router valida arquivo PDF
   ↓
3. ContratoService extrai dados e salva
   ↓
4. Retorna contrato_id
   ↓
5. Cliente faz POST /geolocalizacao/analisar {contrato_id}
   ↓
6. GeolocalizacaoService busca contrato + bureau
   ↓
7. Calcula distância (Haversine)
   ↓
8. Aplica regras de parecer
   ↓
9. Salva resultado em pareceres
   ↓
10. Retorna análise completa
```

### Fluxo 2: Listagem de Pareceres

```
1. Cliente faz GET /pareceres?skip=0&limit=10&tipo=PROXIMAL
   ↓
2. Router passa para PareceService.listar()
   ↓
3. Service aplica filtros no banco
   ↓
4. Retorna lista paginada
```

---

## 🛡️ Tratamento de Erros

### Exception Handlers Necessários

```python
# backend/app/core/exceptions.py

class APIException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class ContratoNaoEncontrado(APIException):
    def __init__(self):
        super().__init__(404, "Contrato não encontrado")

class ArquivoInvalido(APIException):
    def __init__(self):
        super().__init__(400, "Arquivo PDF inválido")

class DadosInsuficientes(APIException):
    def __init__(self):
        super().__init__(422, "Dados insuficientes para análise")

class ServicoGeoloc Indisponivel(APIException):
    def __init__(self):
        super().__init__(503, "Serviço de geolocalização indisponível")

# Registrar em main.py:
@app.exception_handler(APIException)
async def api_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### Códigos de Status HTTP Esperados

- `200 OK` - Sucesso em GET/POST
- `201 Created` - Recurso criado (POST)
- `204 No Content` - Deleção bem-sucedida
- `400 Bad Request` - Dados inválidos
- `403 Forbidden` - Sem permissão
- `404 Not Found` - Recurso não encontrado
- `422 Unprocessable Entity` - Validação falhou
- `500 Internal Server Error` - Erro interno
- `503 Service Unavailable` - Serviço indisponível

---

## 🔐 Segurança

### Autenticação

```python
# Implementar em backend/app/api/dependencies.py

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> int:
    """
    Valida token JWT e retorna user_id
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado ou inválido")
    return user_id

async def get_db(request: Request) -> Generator:
    """
    Injeta sessão de banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Validação de Permissões

```python
# Exemplo: Verificar se usuário é dono do contrato

async def verify_contrato_ownership(
    contrato_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    contrato = db.query(DadosContrato).filter_by(id=contrato_id).first()
    if not contrato or contrato.usuario_id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    return contrato
```

---

## 📝 Resumo de Implementação

### Arquivos a Criar

| Arquivo | Linhas Est. | Dependências |
|---------|-------------|--------------|
| contratos.py | 120-150 | ContratoService, ContratoRepository |
| bureau.py | 80-100 | BureauService, BureauRepository |
| geolocalizacao.py | 100-130 | GeolocalizacaoService |
| pareceres.py | 120-150 | PareceService, PareceRepository |
| health.py | 30-40 | Nenhuma |
| api/v1/__init__.py | 20-30 | Routers |
| dependencies.py | 50-70 | JWT, Database |
| core/exceptions.py | 40-60 | FastAPI |
| Modificações: main.py | +20-30 | Include routers |

**Total estimado:** 600-850 linhas de código

### Dependências Externas Necessárias

```python
# requirements.txt - ADICIONAR:
python-multipart==0.0.6  # Para upload de arquivos
```

---

## ✅ Checklist de Implementação

- [ ] Criar arquivo `backend/app/api/dependencies.py`
- [ ] Criar arquivo `backend/app/core/exceptions.py`
- [ ] Criar arquivo `backend/app/api/v1/__init__.py`
- [ ] Criar arquivo `backend/app/api/v1/contratos.py`
- [ ] Criar arquivo `backend/app/api/v1/bureau.py`
- [ ] Criar arquivo `backend/app/api/v1/geolocalizacao.py`
- [ ] Criar arquivo `backend/app/api/v1/pareceres.py`
- [ ] Criar arquivo `backend/app/api/v1/health.py`
- [ ] Modificar `backend/app/main.py` para incluir routers
- [ ] Adicionar `python-multipart` em requirements.txt
- [ ] Testar todos os endpoints com curl/Postman
- [ ] Gerar documentação Swagger (automático)

---

**Última Atualização:** 02/02/2026  
**Próximo Documento:** Lista de Tarefas (manage_todo_list)

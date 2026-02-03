# Roadmap - Sistema de Laudos
## MVP: Ferramenta de Geolocalização

---

## FASE 1: PREPARAÇÃO E CONFIGURAÇÃO DO SERVIDOR
**Duração Estimada:** 1-2 dias
**Responsável:** DevOps/Infraestrutura

### 1.1 Setup do Servidor Ubuntu
- [X] Provisionar instância Ubuntu 24.04 LTS (ou 22.04)
- [X] Configurar SSH e acesso seguro
- [X] Atualizar sistema operacional e pacotes (`apt update && apt upgrade`)
- [X] Configurar firewall (UFW)
- [X] Configurar timezone e NTP

### 1.2 Instalação de Dependências do Sistema
- [X] Instalar Docker e Docker Compose
- [X] Instalar Python 3.12
- [X] Instalar Git
- [X] Instalar Nginx
- [X] Instalar Node.js (para frontend build)

### 1.3 Configuração de Repositório
- [X] Clonar repositório do projeto
- [X] Configurar SSH keys para acesso ao Git
- [X] Criar estrutura de diretórios do projeto

---

## FASE 2: INFRAESTRUTURA COM DOCKER
**Duração Estimada:** 2-3 dias
**Responsável:** DevOps/Backend

### 2.1 Docker Compose Setup
- [X] Criar arquivo `docker-compose.yml` com serviços:
  - PostgreSQL 16
  - Redis
  - Keycloak (Auth)
  - nginx
  - Backend (FastAPI)
  - Frontend (React)
  
### 2.2 Configuração de Volumes e Redes
- [X] Configurar volumes para persistência (DB, Redis)
- [X] Configurar rede Docker para comunicação entre serviços
- [X] Configurar variáveis de ambiente (`.env`)

### 2.3 Nginx como Reverse Proxy
- [] Configurar Nginx como proxy para FastAPI
- [] Configurar proxy para React (desenvolvimento)
- [] Configurar SSL/TLS (certificado auto-assinado ou Let's Encrypt)

### 2.4 Banco de Dados Inicial
- [ ] Inicializar PostgreSQL via Docker
- [ ] Criar banco de dados `sistema_de_laudos`
- [ ] Criar usuário com permissões apropriadas

---

## FASE 3: CONFIGURAÇÃO DO BANCO DE DADOS
**Duração Estimada:** 2-3 dias
**Responsável:** Backend/DBA

### 3.1 Schema Design (Alembic)
- [X] Configurar Alembic para migrations
- [X] Criar migration inicial com tabelas:
  - [X] `usuarios` - Usuários do sistema
  - [X] `dados_contrato` - Informações extraídas do PDF do contrato
  - [X] `dados_bureau` - Informações do cliente de bureau externo
  - [X] `pareceres` - Análises e pareceres gerados
  - [X] `logs_analise` - Rastreamento de análises

### 3.2 Criar Tabelas (Primeira Iteração - MVP)

#### Tabela: `dados_contrato`
```sql
- id (PK)
- usuario_id (FK)
- cpf_cliente
- numero_contrato
- latitude (coordenada do endereço de assinatura)
- longitude (coordenada do endereço de assinatura)
- endereco_assinatura
- data_upload
- arquivo_pdf_path
- status
- criado_em
- atualizado_em
```

#### Tabela: `dados_bureau`
```sql
- id (PK)
- contrato_id (FK)
- cpf_cliente (chave de busca)
- nome_cliente
- logradouro
- telefone
- cep
- latitude (geocoding do logradouro)
- longitude (geocoding do logradouro)
- data_consulta
- criado_em
```

#### Tabela: `pareceres`
```sql
- id (PK)
- contrato_id (FK)
- distancia_km
- tipo_parecer (enum: PROXIMAL, MODERADO, DISTANTE, MUITO_DISTANTE)
- texto_parecer
- latitude_inicio
- longitude_inicio
- latitude_fim
- longitude_fim
- criado_em
```

### 3.3 Índices e Otimizações
- [X] Criar índices nas FKs e campos de busca frequente (37 índices criados)
- [X] Configurar constraints e validações (5 Foreign Keys com CASCADE DELETE)

---

## FASE 4: DESENVOLVIMENTO DO BACKEND (FastAPI)
**Duração Estimada:** 5-7 dias
**Responsável:** Backend Developer

### 4.1 Estrutura do Projeto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py (inicialização FastAPI)
│   ├── config.py (configurações)
│   ├── core/
│   │   ├── security.py (Keycloak/OAuth2)
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── contratos.py
│   │   │   ├── bureau.py
│   │   │   ├── geolocalização.py
│   │   │   └── pareceres.py
│   │   └── schemas/ (DTOs Pydantic)
│   │       ├── contrato_schema.py
│   │       ├── bureau_schema.py
│   │       ├── geolocation_schema.py
│   │       └── parecer_schema.py
│   ├── services/ (Lógica de negócio)
│   │   ├── contrato_service.py
│   │   ├── bureau_service.py
│   │   ├── geolocation_service.py
│   │   └── parecer_service.py
│   ├── models/ (SQLAlchemy ORM)
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── contrato.py
│   │   ├── bureau.py
│   │   └── parecer.py
│   ├── repositories/ (Data Access Layer)
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── contrato_repository.py
│   │   ├── bureau_repository.py
│   │   └── parecer_repository.py
│   ├── tasks/ (Celery)
│   │   ├── __init__.py
│   │   ├── extract_pdf_task.py
│   │   ├── bureau_lookup_task.py
│   │   └── geolocation_task.py
│   └── utils/
│       ├── pdf_extractor.py (PyMuPDF)
│       ├── nominatim_client.py (Geocoding)
│       ├── distance_calculator.py (Haversine)
│       └── parecer_rules.py (Regras de parecer)
├── migrations/ (Alembic)
├── requirements.txt
├── Dockerfile
└── .env.example
```

### 4.2 Dependências Python (requirements.txt)
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.4.2
pydantic-settings==2.0.3
python-multipart==0.0.6
python-keycloak==0.28.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
celery[redis]==5.3.4
redis==5.0.1
requests==2.31.0
httpx==0.25.2
pymupdf==1.23.5
pdfplumber==0.10.3
geopy==2.3.0
haversine==2.7.0
nominatim-py==0.3.0
pytest==7.4.3
pytest-asyncio==0.21.1
```

### 4.3 Desenvolvimento dos Endpoints MVP

#### 4.3.1 Upload de Contrato
```
POST /api/v1/contratos/upload
- Receber arquivo PDF
- Extrair CPF, número do contrato, coordenadas
- Salvar em dados_contrato
- Retornar ID do contrato
- Disparar task async de busca em bureau
```

#### 4.3.2 Busca em Bureau (Async/Celery)
```
Task: bureau_lookup_task
- Receber ID do contrato
- Buscar dados do cliente (CPF) em MySQL externo
- Geocodificar endereço (Nominatim)
- Salvar em dados_bureau
- Disparar task de análise de geolocalização
```

#### 4.3.3 Análise de Geolocalização
```
GET /api/v1/geolocalizacao/{contrato_id}
- Buscar dados_contrato e dados_bureau
- Calcular distância (Haversine)
- Aplicar regras de parecer
- Salvar parecer em pareceres
- Retornar objeto com:
  {
    contrato_id: int,
    endereco_origem: str,
    endereco_destino: str,
    latitude_origem: float,
    longitude_origem: float,
    latitude_destino: float,
    longitude_destino: float,
    distancia_km: float,
    tipo_parecer: str,
    texto_parecer: str,
    rota: [[lat, lng], ...],
    timestamp: datetime
  }
```

#### 4.3.4 Listagem de Pareceres
```
GET /api/v1/pareceres?page=1&limit=10
- Retornar pareceres gerados com paginação
- Filtrar por data, tipo, usuário
```

### 4.4 Pydantic Schemas (DTOs)
**Status:** ✅ CONCLUÍDO (Phase 4.1)
- [X] Implementar schemas Pydantic para validação
  - [X] UsuarioCreate, Update, Response, List
  - [X] DadosContratoCreate, Update, Response, List
  - [X] DadosBureauCreate, Update, Response, List
  - [X] PareceCreate, Update, Response, List, Filter
  - [X] GeolocationRequest, Analysis, Distance
  - [X] LogsAnaliseCreate, Response, List, Filter
- [X] Validação de email (EmailStr)
- [X] Validação de CPF (regex pattern)
- [X] Validação de CEP (regex pattern)
- [X] Validação de tipos enum

### 4.5 Repositories (Data Access Layer)
**Status:** ✅ CONCLUÍDO (Phase 4.2)
- [X] Implementar BaseRepository[T] com CRUD genérico (7 methods)
  - [X] UsuarioRepository (7 custom methods)
  - [X] ContratoRepository (9 custom methods)
  - [X] BureauRepository (8 custom methods)
  - [X] PareceRepository (11 custom methods)
  - [X] LogsAnaliseRepository (9 custom methods)
- [X] Padrão de retorno: tuple[List[T], int] para paginação
- [X] Queries otimizadas com índices de banco

### 4.6 Utilities (Funcionalidades Auxiliares)
**Status:** ✅ CONCLUÍDO (Phase 4.3 - Utilities)
- [X] Implementar `distance_calculator.py` (Haversine)
  - [X] Calcular distância entre dois pontos
  - [X] Determinar tipo de parecer por distância
  - [X] Gerar texto contextualizado do parecer
- [X] Implementar `nominatim_client.py`
  - [X] Geocodificar endereço (async/sync)
  - [X] Reverse geocodificar coordenadas
  - [X] Rate limiting e tratamento de erros

### 4.7 Services Layer (Business Logic)
**Status:** ✅ CONCLUÍDO (Phase 4.3)
**Data de Conclusão:** 02/02/2026
**Entregáveis:** 5 serviços, 34 métodos, 1.500+ linhas de código
- [X] BaseService (3 métodos)
  - [X] log_info, log_error, log_warning
- [X] ContratoService (9 métodos)
  - [X] CRUD, busca, atualização de status e localização
- [X] BureauService (9 métodos)
  - [X] CRUD, busca, geocodificação automática
- [X] GeolocalizacaoService (6 métodos)
  - [X] Orquestrador principal de análise
  - [X] Cálculo de distância (Haversine)
  - [X] Geocodificação e reverse geocoding
- [X] PareceService (10 métodos)
  - [X] CRUD, filtros avançados, estatísticas

### 4.8 API Endpoints (FastAPI Routes)
**Status:** ⏳ TODO (Phase 4.4)
**Próxima Fase - Em Planejamento**
- [ ] Controllers/Routers para contratos
  - [ ] POST /api/v1/contratos/upload
  - [ ] GET /api/v1/contratos/{id}
  - [ ] GET /api/v1/contratos?usuario_id=X
  - [ ] GET /api/v1/contratos/search?q=term
  - [ ] PUT /api/v1/contratos/{id}/status
  - [ ] PUT /api/v1/contratos/{id}/localizacao
- [ ] Controllers/Routers para geolocalização
  - [ ] POST /api/v1/geolocalizacao/analisar
  - [ ] GET /api/v1/geolocalizacao/estatisticas
- [ ] Controllers/Routers para bureau
  - [ ] GET /api/v1/bureau/{id}
  - [ ] POST /api/v1/bureau/{id}/geocodificar
  - [ ] GET /api/v1/bureau/sem-localizacao
- [ ] Controllers/Routers para pareceres
  - [ ] GET /api/v1/pareceres
  - [ ] GET /api/v1/pareceres/{id}
  - [ ] GET /api/v1/pareceres/tipo?tipo=PROXIMAL
  - [ ] GET /api/v1/pareceres/distancia?min=0&max=50

### 4.9 Autenticação e Autorização
- [ ] Integração Keycloak/OAuth2
- [ ] Middleware de autenticação
- [ ] RBAC (Role-Based Access Control)
- [ ] Proteção de endpoints com `@require_auth`

### 4.10 Logging e Tratamento de Erros
- [ ] Configurar logging estruturado
- [ ] Implementar tratamento de exceções customizadas
- [ ] Health check endpoint `/health`

### 4.11 Testes Unitários
- [ ] Testes para services
- [ ] Testes para repositories
- [ ] Testes para utils (cálculos, formatações)
- [ ] Testes de endpoints (200, 400, 401, 404)

---

## FASE 5: DESENVOLVIMENTO DO FRONTEND (React + Vite)
**Duração Estimada:** 5-7 dias
**Responsável:** Frontend Developer

### 5.1 Estrutura do Projeto

```
frontend/
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── App.css
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── Footer.jsx
│   │   ├── Geolocalização/
│   │   │   ├── UploadContrato.jsx
│   │   │   ├── MapaRota.jsx
│   │   │   ├── PareceresView.jsx
│   │   │   └── ResultadoAnalise.jsx
│   │   └── Common/
│   │       ├── Loading.jsx
│   │       ├── ErrorAlert.jsx
│   │       └── SuccessAlert.jsx
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Geolocalizacao.jsx
│   │   └── Dashboard.jsx
│   ├── services/
│   │   ├── api.js (axios config)
│   │   ├── contratoService.js
│   │   ├── geolocalizacaoService.js
│   │   └── pareceresService.js
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useContrato.js
│   │   └── useGeolocalização.js
│   ├── context/
│   │   ├── AuthContext.jsx
│   │   └── AppContext.jsx
│   ├── styles/
│   │   ├── globals.css
│   │   ├── variables.css
│   │   └── animations.css
│   └── utils/
│       └── helpers.js
├── public/
├── package.json
├── vite.config.js
└── Dockerfile
```

### 5.2 Dependências (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "leaflet": "^1.9.4",
    "react-leaflet": "^4.2.1",
    "@tanstack/react-query": "^5.25.0",
    "zustand": "^4.4.1",
    "classnames": "^2.3.2"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.32"
  }
}
```

### 5.3 Páginas MVP

#### 5.3.1 Página: Upload de Contrato
- [ ] Componente `UploadContrato.jsx`
  - Drag & drop de PDF
  - Validação de arquivo
  - Chamada API POST `/api/v1/contratos/upload`
  - Feedback de progresso
  - Redirect para página de análise após sucesso

#### 5.3.2 Página: Mapa e Geolocalização
- [ ] Componente `MapaRota.jsx`
  - Integração Leaflet
  - Plotar dois marcadores (origem e destino)
  - Desenhar rota entre pontos
  - Exibir distância em KM
  - Zoom automático para ajustar aos marcadores

#### 5.3.3 Página: Resultado da Análise
- [ ] Componente `ResultadoAnalise.jsx`
  - Exibir parecer gerado
  - Mostrar informações do cliente
  - Exibir mapa com rota
  - Botão de exportação para PDF (future)
  - Botão de edição do parecer (future)

#### 5.3.4 Dashboard de Pareceres
- [ ] Página `Dashboard.jsx`
  - Lista de pareceres anteriores com paginação
  - Filtros por data e status
  - Acesso rápido para reabrir análises

### 5.4 Integração com API
- [ ] Configurar axios com base URL
- [ ] Autenticação via token JWT
- [ ] Interceptores para refresh de token
- [ ] Tratamento de erros HTTP

### 5.5 Estado da Aplicação
- [ ] Context ou Zustand para:
  - Autenticação (user, token)
  - Dados do contrato atual
  - Status de carregamento
  - Notificações

### 5.6 Responsividade
- [ ] CSS Grid e Flexbox
- [ ] Mobile-first design
- [ ] Media queries para tablets e desktops

### 5.7 Acessibilidade
- [ ] Atributos ARIA
- [ ] Navegação por teclado
- [ ] Contraste de cores adequado

---

## FASE 6: INTEGRAÇÃO E TESTES
**Duração Estimada:** 3-4 dias
**Responsável:** QA/Full-Stack

### 6.1 Testes End-to-End (E2E)
- [ ] Configurar Playwright ou Cypress
- [ ] Teste completo: Upload → Análise → Visualização
- [ ] Testes de validação de entrada
- [ ] Testes de erros (arquivo inválido, bureau indisponível)

### 6.2 Testes de Performance
- [ ] Medir tempo de upload
- [ ] Medir tempo de análise
- [ ] Load testing da API (Apache JMeter)
- [ ] Verificar cache em Redis

### 6.3 Testes de Segurança
- [ ] Validar autenticação OAuth2
- [ ] Testar CORS
- [ ] Verificar proteção CSRF
- [ ] SQL Injection tests
- [ ] Rate limiting

### 6.4 Integração Bureau Externo
- [ ] Conectar com base MySQL de bureau (se disponível)
  - Credentials seguros em `.env`
  - Retry logic
  - Fallback em caso de indisponibilidade

---

## FASE 7: DEPLOYMENT E PRODUÇÃO
**Duração Estimada:** 2-3 dias
**Responsável:** DevOps

### 7.1 Build e Deploy
- [ ] Build Docker images:
  - Backend (FastAPI)
  - Frontend (React compiled)
  - Nginx

### 7.2 Orquestração
- [ ] Configurar docker-compose.yml para produção
- [ ] Variáveis de ambiente seguras
- [ ] Volumes persistentes para DB

### 7.3 Monitoramento
- [ ] Health checks nos containers
- [ ] Logs centralizados (ELK stack, opcional)
- [ ] Alertas para falhas

### 7.4 Backup e Recuperação
- [ ] Estratégia de backup do PostgreSQL
- [ ] Testes de restore

### 7.5 CI/CD (Opcional para MVP)
- [ ] GitHub Actions ou GitLab CI
- [ ] Pipeline de build e deploy automático
- [ ] Testes automatizados no pipeline

---

## FASE 8: DOCUMENTAÇÃO E HANDOVER
**Duração Estimada:** 1-2 dias
**Responsável:** Tech Lead/Documentação

### 8.1 Documentação Técnica
- [ ] API docs (Swagger/OpenAPI auto-gerado pelo FastAPI)
- [ ] Database schema documentation
- [ ] Architecture decision records (ADRs)
- [ ] Setup local para novos developers

### 8.2 Documentação do Usuário
- [ ] Manual de uso do sistema
- [ ] Screenshots e guias de passo a passo
- [ ] FAQ e troubleshooting

### 8.3 Runbooks
- [ ] Procedimento de deploy
- [ ] Checklist de go-live
- [ ] Escalation procedures

---

## TIMELINE ESTIMADA DO MVP

| Fase | Duração | Data Conclusão | Status | Progresso |
|------|---------|----------------|--------|----------|
| 1. Infraestrutura Servidor | 1-2 dias | ✅ | ✅ Concluída | 100% |
| 2. Docker Setup | 2-3 dias | ✅ | ✅ Concluída | 100% |
| 3. Banco de Dados | 2-3 dias | ✅ | ✅ Concluída | 100% |
| 4.1 Pydantic Schemas | 1-2 dias | ✅ | ✅ Concluída | 100% |
| 4.2 Repositories | 2-3 dias | ✅ | ✅ Concluída | 100% |
| 4.3 Services Layer | 2-3 dias | ✅ 02/02/2026 | ✅ Concluída | 100% |
| 4.4 API Endpoints | 2-3 dias | ⏳ | ⏳ Em Planejamento | 0% |
| 5. Frontend | 5-7 dias | ⏳ | ⏳ Aguardando | 0% |
| 6. Testes e Integração | 3-4 dias | ⏳ | ⏳ Aguardando | 0% |
| 7. Deploy | 2-3 dias | ⏳ | ⏳ Aguardando | 0% |
| 8. Documentação | 1-2 dias | ⏳ | ⏳ Aguardando | 0% |
| **TOTAL** | **~4 semanas** | | **✅ 67% Concluída** | **67%** |

---

## CHECKPOINTS E CRITÉRIOS DE SUCESSO

### Checkpoint 1: Infraestrutura OK
- [X] Servidor UP e acessível via SSH
- [X] Docker Compose rodando todos os serviços
- [X] PostgreSQL com schema criado

### Checkpoint 2: Backend Funcional
- [ ] Upload de PDF OK
- [ ] Extração de dados OK
- [ ] Cálculo de distância OK
- [ ] API respondendo com dados corretos
- [ ] Testes unitários passando

**Status Checkpoint 2 (Em Progresso):**
- [X] Database schema completo (5 tabelas, 37 índices)
- [X] Models SQLAlchemy configurados
- [X] Alembic migrations funcionando
- [X] Foreign keys e constraints em place
- [X] Pydantic schemas para validação (20+ schemas)
- [X] Repositories para acesso a dados (6 classes, 51 métodos)
- [X] Utilities para geocodificação e cálculos
- [X] Services Layer completa (5 serviços, 34 métodos)
- [ ] API Endpoints implementados
- [ ] Documentação Swagger automática

### Checkpoint 3: Frontend Funcional
- [ ] Interface de upload OK
- [ ] Mapa renderizando corretamente
- [ ] Parecer sendo exibido
- [ ] Responsividade OK

### Checkpoint 4: MVP Completo
- [ ] Fluxo end-to-end funcionando
- [ ] Testes E2E passando
- [ ] Sistema em produção
- [ ] Documentação completa

---

## RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|--------|-----------|
| Bureau externo indisponível | Média | Alto | Implementar retry logic e fallback; mock data para testes |
| Nominatim rate-limiting | Média | Médio | Configurar cache em Redis; usar self-hosted Nominatim se necessário |
| Performance de PDF grande | Baixa | Médio | Implementar queue assíncrona (Celery) |
| Delay em integração Auth | Média | Médio | Usar mock auth para MVP; integrar Keycloak mais tarde |

---

## PRÓXIMAS FUNCIONALIDADES (Backlog Futuro)

1. Edição manual de laudo
2. Upload de prints/imagens
3. Editor rich-text (Quill/TipTap)
4. Geração de PDF
5. Histórico de versões do laudo
6. Coleta de múltiplas fontes de dados
7. Dashboard analítico


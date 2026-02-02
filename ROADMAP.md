# Roadmap - Sistema de Laudos
## MVP: Ferramenta de Geolocalização

---

## FASE 1: PREPARAÇÃO E CONFIGURAÇÃO DO SERVIDOR
**Duração Estimada:** 1-2 dias
**Responsável:** DevOps/Infraestrutura

### 1.1 Setup do Servidor Ubuntu
- [ ] Provisionar instância Ubuntu 24.04 LTS (ou 22.04)
- [ ] Configurar SSH e acesso seguro
- [ ] Atualizar sistema operacional e pacotes (`apt update && apt upgrade`)
- [ ] Configurar firewall (UFW)
- [ ] Configurar timezone e NTP

### 1.2 Instalação de Dependências do Sistema
- [ ] Instalar Docker e Docker Compose
- [ ] Instalar Python 3.12
- [ ] Instalar Git
- [ ] Instalar Nginx
- [ ] Instalar Node.js (para frontend build)

### 1.3 Configuração de Repositório
- [ ] Clonar repositório do projeto
- [ ] Configurar SSH keys para acesso ao Git
- [ ] Criar estrutura de diretórios do projeto

---

## FASE 2: INFRAESTRUTURA COM DOCKER
**Duração Estimada:** 2-3 dias
**Responsável:** DevOps/Backend

### 2.1 Docker Compose Setup
- [ ] Criar arquivo `docker-compose.yml` com serviços:
  - PostgreSQL 16
  - Redis
  - Keycloak (Auth)
  - nginx
  - Backend (FastAPI)
  - Frontend (React)
  
### 2.2 Configuração de Volumes e Redes
- [ ] Configurar volumes para persistência (DB, Redis)
- [ ] Configurar rede Docker para comunicação entre serviços
- [ ] Configurar variáveis de ambiente (`.env`)

### 2.3 Nginx como Reverse Proxy
- [ ] Configurar Nginx como proxy para FastAPI
- [ ] Configurar proxy para React (desenvolvimento)
- [ ] Configurar SSL/TLS (certificado auto-assinado ou Let's Encrypt)

### 2.4 Banco de Dados Inicial
- [ ] Inicializar PostgreSQL via Docker
- [ ] Criar banco de dados `sistema_de_laudos`
- [ ] Criar usuário com permissões apropriadas

---

## FASE 3: CONFIGURAÇÃO DO BANCO DE DADOS
**Duração Estimada:** 2-3 dias
**Responsável:** Backend/DBA

### 3.1 Schema Design (Alembic)
- [ ] Configurar Alembic para migrations
- [ ] Criar migration inicial com tabelas:
  - `usuarios` - Usuários do sistema
  - `dados_contrato` - Informações extraídas do PDF do contrato
  - `dados_bureau` - Informações do cliente de bureau externo
  - `pareceres` - Análises e pareceres gerados
  - `logs_analise` - Rastreamento de análises

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
- [ ] Criar índices nas FKs e campos de busca frequente
- [ ] Configurar constraints e validações

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

### 4.4 Implementação de Serviços Chave

#### 4.4.1 PDF Extractor
- [ ] Implementar `pdf_extractor.py` usando PyMuPDF
  - Extrair texto
  - Detectar CPF (regex)
  - Detectar número do contrato
  - OCR de assinatura com coordenadas

#### 4.4.2 Nominatim Client
- [ ] Implementar `nominatim_client.py`
  - Converter endereço → lat/lng
  - Cache de resultados em Redis
  - Rate limiting (1 req/s)

#### 4.4.3 Distance Calculator
- [ ] Implementar `distance_calculator.py` (Haversine)
  - Calcular distância entre dois pontos

#### 4.4.4 Parecer Rules Engine
- [ ] Implementar `parecer_rules.py`
  - Até 5 km: PROXIMAL
  - 5-20 km: MODERADO
  - 20-50 km: DISTANTE
  - Acima de 50 km: MUITO_DISTANTE
  - Gerar texto automático baseado na distância

### 4.5 Autenticação e Autorização
- [ ] Integração Keycloak/OAuth2
- [ ] Middleware de autenticação
- [ ] RBAC (Role-Based Access Control)
- [ ] Proteção de endpoints com `@require_auth`

### 4.6 Logging e Tratamento de Erros
- [ ] Configurar logging estruturado
- [ ] Implementar tratamento de exceções customizadas
- [ ] Health check endpoint `/health`

### 4.7 Testes Unitários
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

| Fase | Duração | Início | Fim |
|------|---------|--------|-----|
| 1. Infraestrutura Servidor | 1-2 dias | Dia 1 | Dia 2 |
| 2. Docker Setup | 2-3 dias | Dia 3 | Dia 5 |
| 3. Banco de Dados | 2-3 dias | Dia 5 | Dia 7 |
| 4. Backend | 5-7 dias | Dia 8 | Dia 14 |
| 5. Frontend | 5-7 dias | Dia 8 | Dia 14 (paralelo) |
| 6. Testes e Integração | 3-4 dias | Dia 15 | Dia 18 |
| 7. Deploy | 2-3 dias | Dia 19 | Dia 21 |
| 8. Documentação | 1-2 dias | Dia 22 | Dia 23 |
| **TOTAL** | **~4 semanas** | | |

---

## CHECKPOINTS E CRITÉRIOS DE SUCESSO

### Checkpoint 1: Infraestrutura OK
- [ ] Servidor UP e acessível via SSH
- [ ] Docker Compose rodando todos os serviços
- [ ] PostgreSQL com schema criado

### Checkpoint 2: Backend Funcional
- [ ] Upload de PDF OK
- [ ] Extração de dados OK
- [ ] Cálculo de distância OK
- [ ] API respondendo com dados corretos
- [ ] Testes unitários passando

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


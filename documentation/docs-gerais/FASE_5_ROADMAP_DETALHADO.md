# FASE 5 - FRONTEND REACT DEVELOPMENT
## Plano Detalhado e Roadmap

**Data Início:** 03/02/2026  
**Status:** ✅ Iniciado  
**Duração Estimada:** 5-7 dias  
**Objetivo:** Implementar frontend React completo com integração ao Backend

---

## 📊 ESTRUTURA DA FASE 5

```
FASE 5: Frontend React Development (5-7 dias)
├── Task 5.1: Layout Base & Navigation (1-2 dias)
├── Task 5.2: Componentes de Upload (1-2 dias)
├── Task 5.3: Componentes de Listagem (1-2 dias)
├── Task 5.4: Componentes de Mapa (1-2 dias)
├── Task 5.5: Componentes de Resultado (1 dia)
└── Task 5.6: Integração com Backend API (1 dia)

FASE 6: Testes E2E (3-4 dias) - Próximo
FASE 7: Deploy em Produção (2-3 dias) - Depois
FASE 8: Documentação (1-2 dias) - Final
```

---

## 🎯 TASK 5.1: LAYOUT BASE & NAVIGATION (1-2 DIAS)

### Objetivos
- ✅ Criar estrutura de pastas para componentes
- ✅ Implementar Navbar responsivo
- ✅ Implementar Sidebar/Menu lateral
- ✅ Criar Footer
- ✅ Implementar Layout principal com Grid
- ✅ Adicionar Tailwind CSS configuração
- ✅ Adicionar React Router com rotas básicas

### Arquivos a Criar

```
src/
├── components/
│   ├── layouts/
│   │   ├── MainLayout.jsx        [Layout principal com Navbar + Sidebar + Footer]
│   │   ├── MainLayout.module.css [Estilos do layout]
│   ├── navbar/
│   │   ├── Navbar.jsx            [Barra de navegação topo]
│   │   ├── Navbar.module.css     [Estilos navbar]
│   ├── sidebar/
│   │   ├── Sidebar.jsx           [Menu lateral]
│   │   ├── Sidebar.module.css    [Estilos sidebar]
│   ├── footer/
│   │   ├── Footer.jsx            [Rodapé]
│   │   ├── Footer.module.css     [Estilos footer]
├── pages/
│   ├── Home.jsx                  [Página inicial]
│   ├── Upload.jsx                [Página de upload]
│   ├── Contratos.jsx             [Página de listagem]
│   ├── Resultado.jsx             [Página de resultado]
├── styles/
│   ├── tailwind.css              [Configuração Tailwind]
│   ├── globals.css               [Estilos globais]
├── App.jsx                       [Atualizar com rotas]
├── main.jsx                      [Entry point]
```

### Componentes Específicos

#### Navbar
```jsx
// Elementos:
- Logo/Título "Sistema de Laudos"
- Menu items (Home, Upload, Contratos, Sobre)
- Ícone usuário com dropdown
- Ícone notificações (placeholder)
- Responsivo (hamburguer em mobile)
```

#### Sidebar
```jsx
// Elementos:
- Menu principal (4-5 itens)
- Ícone + Label para cada item
- Collapse/Expand
- Highlight do item ativo
- Animações smooth
```

#### Footer
```jsx
// Elementos:
- Texto copyright
- Links úteis (Docs, GitHub, Contato)
- Informações de versão
- Status da API
```

#### MainLayout
```jsx
// Grid:
- Header (80px) - Navbar
- Container com 2 colunas:
  ├─ Sidebar (250px fixed)
  └─ Main Content (flex-grow)
- Footer (60px)
```

### Configurações

#### tailwind.config.js
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#007bff',
        secondary: '#6c757d',
        success: '#28a745',
        danger: '#dc3545',
        warning: '#ffc107',
      }
    }
  },
  plugins: [],
}
```

#### Routes
```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'

const routes = [
  { path: '/', component: 'Home' },
  { path: '/upload', component: 'Upload' },
  { path: '/contratos', component: 'Contratos' },
  { path: '/resultado/:id', component: 'Resultado' },
]
```

### Checklist Task 5.1
- [ ] Criar estrutura de pastas
- [ ] Instalar/configurar Tailwind CSS
- [ ] Criar componente Navbar
- [ ] Criar componente Sidebar
- [ ] Criar componente Footer
- [ ] Criar componente MainLayout
- [ ] Configurar React Router
- [ ] Criar páginas base
- [ ] Implementar responsividade
- [ ] Testar navegação

---

## 📤 TASK 5.2: COMPONENTES DE UPLOAD (1-2 DIAS)

### Objetivos
- ✅ Criar componente Drag & Drop
- ✅ Validação de arquivo (PDF)
- ✅ Progress bar para upload
- ✅ Integração com API /api/v1/contratos/upload
- ✅ Feedback visual (sucesso/erro)

### Componentes

```
src/components/upload/
├── UploadArea.jsx           [Área de drag & drop]
├── FileInput.jsx            [Input de arquivo]
├── ProgressBar.jsx          [Barra de progresso]
├── UploadStatus.jsx         [Status/feedback]
```

---

## 📋 TASK 5.3: COMPONENTES DE LISTAGEM (1-2 DIAS)

### Objetivos
- ✅ Tabela de contratos
- ✅ Paginação
- ✅ Filtros (status, data, etc)
- ✅ Busca com debounce
- ✅ Integração com API GET /contratos

### Componentes

```
src/components/contratos/
├── ContratoTable.jsx        [Tabela]
├── TableRow.jsx             [Linha da tabela]
├── Pagination.jsx           [Paginação]
├── Filters.jsx              [Filtros]
├── SearchBox.jsx            [Busca]
```

---

## 🗺️ TASK 5.4: COMPONENTES DE MAPA (1-2 DIAS)

### Objetivos
- ✅ Integrar Leaflet/React-Leaflet
- ✅ Mostrar marcadores de endereço
- ✅ Calcular distância visualmente
- ✅ Zoom automático
- ✅ Integração com API /geolocalizacao

### Componentes

```
src/components/map/
├── MapView.jsx              [Mapa principal]
├── MapMarker.jsx            [Marcador]
├── MapControls.jsx          [Controles]
```

---

## 📊 TASK 5.5: COMPONENTES DE RESULTADO (1 DIA)

### Objetivos
- ✅ Card de parecer
- ✅ Estatísticas
- ✅ Timeline
- ✅ Download de resultado

### Componentes

```
src/components/resultado/
├── ResultCard.jsx           [Card de parecer]
├── Statistics.jsx           [Estatísticas]
├── Timeline.jsx             [Timeline de processamento]
├── DownloadButton.jsx       [Botão download]
```

---

## 🔌 TASK 5.6: INTEGRAÇÃO COM BACKEND (1 DIA)

### Objetivos
- ✅ Service layer com Axios
- ✅ Gestão de tokens (Keycloak)
- ✅ Cache com React Query
- ✅ Tratamento de erros global
- ✅ Interceptadores HTTP

### Arquivos

```
src/services/
├── api.js                   [Instância Axios]
├── contractService.js       [Endpoints contratos]
├── bureauService.js         [Endpoints bureau]
├── geoService.js            [Endpoints geo]
├── pareceService.js         [Endpoints parecer]

src/hooks/
├── useContratos.js          [Hook para contratos]
├── useBureau.js             [Hook para bureau]
├── useGeo.js                [Hook para geo]
├── useParecer.js            [Hook para parecer]

src/store/
├── authStore.js             [Estado autenticação (Zustand)]
├── appStore.js              [Estado global app]
```

---

## 📈 TIMELINE DETALHADA

```
Dia 1:  ✅ Task 5.1.1-5.1.3 (Navbar, Sidebar, Footer)
Dia 2:  ✅ Task 5.1.4-5.1.6 (Layout, Router, Responsividade)
Dia 3:  ✅ Task 5.2 (Upload completo)
Dia 4:  ✅ Task 5.3 (Listagem completa)
Dia 5:  ✅ Task 5.4 (Mapa completo)
Dia 6:  ✅ Task 5.5 + 5.6 (Resultado + API)
Dia 7:  ⏳ Testes, refinamentos, bugfix
```

---

## 🛠️ SETUP INICIAL - TASK 5.1

### Passo 1: Instalar Tailwind CSS
```bash
cd frontend
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Passo 2: Criar Estrutura de Pastas
```bash
mkdir -p src/components/{layouts,navbar,sidebar,footer}
mkdir -p src/pages
mkdir -p src/styles
mkdir -p src/services
mkdir -p src/hooks
mkdir -p src/store
```

### Passo 3: Configurar Tailwind
Atualizar `tailwind.config.js` com cores custom

### Passo 4: Criar Componentes Base
Começar com Navbar → Sidebar → Footer → Layout

### Passo 5: Configurar React Router
Definir rotas principais

### Passo 6: Testar Layout
Navegar entre páginas e validar responsividade

---

## 📚 STACK UTILIZADO

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| React | 18.2.0 | Framework |
| React Router | 6.20 | Navegação |
| Axios | 1.6.2 | HTTP Client |
| Tailwind CSS | 3.4.0 | Estilos |
| Zustand | 4.4.1 | State Mgmt |
| React Query | 5.25 | Data Fetching |
| Leaflet | 1.9.4 | Mapas |
| React Leaflet | 4.2.1 | Integração |

---

## 🎓 PRÓXIMOS PASSOS

1. ✅ Confirmar Fase 5 iniciada
2. ⏳ **COMEÇAR: Task 5.1 - Implementar Layout Base**
3. ⏳ Task 5.1.1 - Navbar
4. ⏳ Task 5.1.2 - Sidebar
5. ⏳ Task 5.1.3 - Footer
6. ⏳ Task 5.1.4 - MainLayout
7. ⏳ Task 5.1.5 - React Router
8. ⏳ Task 5.1.6 - Responsividade

---

**Status Geral:**
- Backend: ✅ 100% completo
- Frontend: 🚀 Iniciando
- Project: 80% → 85% (estimado com Task 5.1)

**Próximo Checkpoint:** Task 5.1 completa (Layout Base com navegação funcional)


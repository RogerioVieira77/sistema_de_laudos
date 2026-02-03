# FASE 5 - Frontend React Development
## Instruções de Acesso ao Frontend Padrão

**Data:** 03/02/2026  
**Status:** ✅ Frontend disponível para testes

---

## 🌐 ACESSO AO FRONTEND

### URL Pública (Internet)
```
http://82.25.75.88:80
http://82.25.75.88/
```

### URLs Locais (Desenvolvimento)
```
http://localhost:80
http://127.0.0.1:80
http://localhost/        (via Nginx proxy)
```

---

## 🔍 STATUS ATUAL DO FRONTEND

### Container Docker
```
Nome: sistema_laudos_frontend_dev
Status: Up 16 hours (healthy) ✅
Imagem: sistema_de_laudos-frontend
Porta Interna: 3000
Porta Exposta: 80 (via Nginx)
```

### Verificação de Saúde
```bash
curl -I http://localhost:80
# HTTP/1.1 200 OK
```

---

## 📁 ESTRUTURA ATUAL DO FRONTEND

```
frontend/
├── package.json          [Configuração de dependências]
├── vite.config.js        [Configuração do Vite]
├── index.html            [HTML principal]
├── Dockerfile            [Containerização]
├── nginx.conf            [Configuração Nginx]
└── src/
    ├── main.jsx          [Entry point React]
    ├── App.jsx           [Componente raiz]
    ├── App.css           [Estilos globais]
    ├── index.css         [CSS principal]
    └── [components/]     [Componentes a serem criados]
```

---

## 📦 DEPENDÊNCIAS INSTALADAS

### React Stack
```
✅ react@18.2.0          [Framework frontend]
✅ react-dom@18.2.0      [Renderização DOM]
✅ react-router-dom@6.20 [Roteamento SPA]
```

### API & State Management
```
✅ axios@1.6.2           [HTTP client]
✅ zustand@4.4.1         [State management]
✅ @tanstack/react-query@5.25 [Data fetching & caching]
```

### Mapa e Localização
```
✅ leaflet@1.9.4         [Biblioteca de mapas]
✅ react-leaflet@4.2.1   [Componentes React para mapas]
```

### Autenticação
```
✅ keycloak-js@23.0.0    [Integração Keycloak]
```

### Utilitários
```
✅ classnames@2.3.2      [Conditional className helper]
✅ tailwindcss@3.4.0     [CSS framework]
```

---

## 🛠️ SCRIPTS DISPONÍVEIS

### Desenvolvimento (Local)
```bash
npm run dev
# Inicia Vite dev server em http://localhost:5173
```

### Produção (Build)
```bash
npm run build
# Cria build otimizado em ./dist
```

### Testes
```bash
npm run preview
# Simula build em localhost:4173
```

### Code Quality
```bash
npm run lint
# Valida código com ESLint

npm run format
# Formata código com Prettier
```

---

## 🎯 COMPONENTES A SEREM DESENVOLVIDOS (Fase 5)

### Task 5.1: Layout Base & Navigation
- [x] Navbar com logo e menu
- [x] Sidebar para navegação
- [x] Footer com informações
- [x] Layout responsivo

### Task 5.2: Componentes de Upload
- [ ] Componente Upload Área (Drag & Drop)
- [ ] Progress bar para upload
- [ ] Validação de arquivo
- [ ] Mensagens de sucesso/erro

### Task 5.3: Componentes de Listagem
- [ ] Tabela de contratos
- [ ] Paginação
- [ ] Filtros avançados
- [ ] Busca com debounce

### Task 5.4: Componentes de Mapa
- [ ] Integração Leaflet
- [ ] Marcadores de endereço
- [ ] Cálculo de distância visual
- [ ] Zoom automático

### Task 5.5: Componentes de Resultado
- [ ] Card de parecer
- [ ] Estatísticas
- [ ] Timeline de processamento
- [ ] Download de resultado

### Task 5.6: Integrações com Backend
- [ ] Service layer para API
- [ ] Gestão de tokens (Keycloak)
- [ ] Cache com React Query
- [ ] Tratamento de erros

---

## 🚀 FLUXO DE TESTES

### 1. Teste de Acesso (Remoto)
```bash
# Abrir no navegador - via servidor público
http://82.25.75.88

# Ou testar via curl
curl -I http://82.25.75.88
# Esperado: HTTP/1.1 200 OK
```

### 1b. Teste de Acesso (Local)
```bash
# Abrir no navegador - localhost
http://localhost:80

# Ou testar via curl
curl -I http://localhost:80
# Esperado: HTTP/1.1 200 OK
```

### 2. Teste de Hot Module Replacement (HMR)
```bash
# Se rodar localmente com npm run dev
# Modificar um arquivo .jsx e salvar
# O navegador atualizará automaticamente
```

### 3. Teste de Build
```bash
npm run build
npm run preview
# Acessar em http://localhost:4173
```

---

## 📝 ARQUIVOS DE CONFIGURAÇÃO

### vite.config.js
```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    watch: { usePolling: true },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
```

### nginx.conf
```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://frontend:3000;
        # ... headers e configurações
    }
}
```

### Dockerfile
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

---

## 🔗 INTEGRAÇÕES

### Backend API (Remoto)
```
Base URL: http://82.25.75.88:8000
Endpoints documentados em: http://82.25.75.88/api/v1/docs
Swagger UI: http://82.25.75.88/api/v1/docs
ReDoc: http://82.25.75.88/api/v1/redoc
Health Check: http://82.25.75.88/api/v1/health
```

### Backend API (Local)
```
Base URL: http://localhost:8000
Endpoints documentados em: http://localhost:8000/api/v1/docs
```

### Autenticação (Keycloak - Remoto)
```
URL: http://82.25.75.88:8080
Realm: sistema-laudos
Client: frontend
Redirect URI: http://82.25.75.88/callback
```

### Autenticação (Keycloak - Local)
```
URL: http://localhost:8080
Realm: sistema-laudos
Client: frontend
Redirect URI: http://localhost/callback
```

### Banco de Dados (via Backend)
```
PostgreSQL: localhost:5432 (acessível via backend apenas)
Redis Cache: localhost:6379 (acessível via backend apenas)
```

---

## ✅ CHECKLIST ANTES DE COMEÇAR

- [x] Frontend rodando (HTTP 200)
- [x] Backend rodando na porta 8000
- [x] Nginx proxy configurado
- [x] Docker compose healthy
- [x] Package.json válido
- [x] Vite configurado corretamente
- [x] Dependências instaladas
- [x] Estrutura de pastas criada
- [ ] **Próximo: Criar componentes iniciais**

---

## 📚 DOCUMENTAÇÃO RELACIONADA

- [Backend API](http://lo (Produção)
```bash
# Criar .env.production na raiz do frontend
VITE_API_BASE_URL=http://82.25.75.88/api/v1
VITE_KEYCLOAK_URL=http://82.25.75.88:8080
VITE_KEYCLOAK_REALM=sistema-laudos
VITE_KEYCLOAK_CLIENT=frontend
```

### Variáveis de Ambiente (Desenvolvimento)
```bash
# Criar .env.local na raiz do frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=sistema-laudos
VITE_KEYCLOAK_CLIENT=frontend
---

## 💡 DICAS DE DESENVOLVIMENTO

### Hot Module Replacement
```javascript
// Adicionar em App.jsx para HMR em desenvolvimento
if (import.meta.hot) {
  import.meta.hot.accept()
}
```

### Variáveis de Ambiente
```bash
# Criar .env.local na raiz do frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_KEYCLOAK_URL=http://localhost:8080
```

### Debug no Console
```javascript
// Adicionar log no console do navegador
console.log('Component mounted')
```

---

## 🆘 TROUBLESHOOTING

### Frontend retorna 500
```bash
# Verificar logs do container
docker logs sistema_laudos_frontend_dev

# Reiniciar container
docker restart sistema_laudos_frontend_dev
```

### Hot Module Replacement não funciona
```bash
# Verificar se Vite está escutando em 0.0.0.0
# vite.config.js deve ter: host: '0.0.0.0'

# Reiniciar com npm run dev se for local
```

### API retorna CORS error
```javascript
// Usar proxy do Nginx em vez de chamada direta
// Já está configurado em nginx.conf
// Endpoints devem ser relativos: /api/v1/...
```

---

## 🎓 PRÓXIMOS PASSOS

1. ✅ Verificar acesso ao frontend (FEITO)
2. ⏳ Task 5.1: Criar Layout Base & Navigation
3. ⏳ Task 5.2: Componentes de Upload
4. ⏳ Task 5.3: Componentes de Listagem
5. ⏳ Task 5.4: Integração com Mapa
6. ⏳ Task 5.5: Componentes de Resultado
7. ⏳ Task 5.6: Integração com Backend API

---

**Frontend Status:** ✅ Pronto para desenvolvimento  
**Data:** 03/02/2026  
**Próxima Etapa:** Iniciar Task 5.1 (Layout Base)

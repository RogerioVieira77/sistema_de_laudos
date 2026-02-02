# ✅ Guia Rápido - Teste Deploy após Correções

**Data:** 02/02/2026  
**Versão:** 1.0.0

---

## 🎯 Objetivo

Verificar se as correções no `docker-compose.yml` funcionam corretamente.

---

## 📋 Pré-requisitos

✅ Arquivo `docker-compose.yml` atualizado (com correções)  
✅ Arquivo `.env.dev` configurado na raiz  
✅ Docker Compose v5.0.2+ instalado

---

## 🚀 Execução Passo a Passo

### Passo 1: Validar docker-compose.yml

```bash
cd /opt/app/sistema_de_laudos

# Validar sintaxe
docker compose config

# Saída esperada: arquivo completo sem erros
```

### Passo 2: Limpar Containers Antigos (se existirem)

```bash
# Parar e remover containers antigos
docker compose down -v

# Ou somente parar (sem remover volumes)
docker compose stop
```

### Passo 3: Build das Imagens

```bash
# Compilar imagens com novo Dockerfile
docker compose build

# Saída esperada:
# [+] Building 10.5s (XX/XX)
# ✔ backend
# ✔ frontend
# ✔ postgres
# ✔ redis
# ✔ keycloak
# ✔ nginx
# ✔ celery
```

### Passo 4: Iniciar Serviços

```bash
# Iniciar todos os containers
docker compose up -d

# Saída esperada:
# [+] Running 7/7
# ✔ Container sistema_de_laudos_postgres_dev       Started
# ✔ Container sistema_laudos_redis_dev             Started
# ✔ Container sistema_laudos_backend_dev           Started
# ✔ Container sistema_laudos_frontend_dev          Started
# ✔ Container sistema_laudos_keycloak_dev          Started
# ✔ Container sistema_laudos_celery_dev            Started
# ✔ Container sistema_laudos_nginx_dev             Started
```

### Passo 5: Monitorar Inicialização

```bash
# Ver status dos containers
docker compose ps

# Acompanhar logs (CTRL+C para sair)
docker compose logs -f --tail=50
```

**Aguarde até que:**
- PostgreSQL = `Up (healthy)`
- Redis = `Up (healthy)`
- Backend = `Up` (com ou sem healthcheck)
- Frontend = `Up`
- Keycloak = `Up` (pode levar 30-60s)
- Celery = `Up`
- Nginx = `Up`

---

## ✅ Teste de Conectividade

### Backend Health Check

```bash
# Verificar se Backend está respondendo
curl http://82.25.75.88:8000/api/v1/health

# Saída esperada:
# {"status":"healthy","service":"Sistema de Laudos Backend","version":"1.0.0"}
```

### Frontend

```bash
# Abrir no navegador
# http://localhost:3000

# Ou testar com curl
curl http://localhost:3000
```

### PostgreSQL

```bash
# Testar conexão
docker compose exec postgres pg_isready -U dbadmin_dev

# Saída esperada: accepting connections
```

### Redis

```bash
# Testar conexão
docker compose exec redis redis-cli -a redisadmin_dev ping

# Saída esperada: PONG
```

### Keycloak

```bash
# Testar saúde
curl http://82.25.75.88:8080/health/ready

# Saída esperada: {"status":"UP"}
```

---

## 🔴 Se Houver Erros

### Backend não inicia

```bash
# Ver logs detalhados
docker compose logs backend

# Se disser "uvicorn not found":
# - Reconstruir sem cache
docker compose build --no-cache backend
docker compose up -d backend
```

### Frontend não carrega

```bash
# Ver logs
docker compose logs frontend

# Reiniciar
docker compose restart frontend
```

### PostgreSQL não conecta

```bash
# Ver logs
docker compose logs postgres

# Reiniciar
docker compose restart postgres
```

---

## 🔧 Verificação de Variáveis de Ambiente

```bash
# Ver variáveis passadas ao Backend
docker inspect sistema_laudos_backend_dev | grep -A 20 "Env"

# Ver variáveis do Frontend
docker inspect sistema_laudos_frontend_dev | grep -A 20 "Env"
```

---

## 📝 Checklist Final

- [ ] `docker compose config` sem erros ✅
- [ ] `docker compose up -d` sucesso ✅
- [ ] Backend health check retorna 200 ✅
- [ ] Frontend carrega em http://82.25.75.88:8080 ✅
- [ ] PostgreSQL respondendo ✅
- [ ] Redis respondendo ✅
- [ ] Keycloak health check OK ✅
- [ ] Celery rodando ✅
- [ ] Nginx rodando ✅

---

## 🎉 Sucesso!

Se todos os testes passarem, o deploy está **pronto para uso em desenvolvimento**.

---

## 📖 Próximos Passos

1. Revisar [Deploy.md](Deploy.md) para configurações adicionais
2. Consultar [ANALISE_INCONSISTENCIAS.md](ANALISE_INCONSISTENCIAS.md) para mais detalhes
3. Executar migrations: `docker compose exec backend alembic upgrade head`
4. Testar funcionalidades da aplicação

---

**Teste rápido criado em:** 02/02/2026

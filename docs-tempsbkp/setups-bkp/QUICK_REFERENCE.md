# 🎯 QUICK REFERENCE - FASE 2 DOCKER

## 🚀 Comandos Essenciais

```bash
# Iniciar tudo
docker-compose up -d

# Parar tudo
docker-compose down

# Ver status
docker-compose ps

# Logs em tempo real
docker-compose logs -f backend
docker-compose logs -f frontend

# Executar comando em um container
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec postgres psql -U laudos_user

# Rebuild de uma imagem
docker-compose build --no-cache backend

# Remover tudo (incluindo dados!)
docker-compose down -v
```

---

## 📍 URLs de Acesso

```
Frontend               http://localhost
Backend API            http://localhost:8000
Swagger Docs           http://localhost:8000/docs
ReDoc                  http://localhost:8000/redoc
Keycloak Admin         http://localhost:8080/admin
Keycloak Realm         http://localhost:8080/realms/sistema_laudos
Flower (Celery)        http://localhost:5555
Nginx                  http://localhost:80
```

---

## 🔐 Credenciais Padrão

| Serviço | User | Password |
|---------|------|----------|
| PostgreSQL | laudos_user | laudos_password_123 |
| Redis | - | redis_password_123 |
| Keycloak | admin | keycloak_admin_123 |
| Demo User | demo | demo123456 |

---

## 📦 Serviços e Portas

```yaml
PostgreSQL:  localhost:5432   # Banco de dados
Redis:       localhost:6379   # Cache
Keycloak:    localhost:8080   # Auth
Backend:     localhost:8000   # API
Frontend:    localhost:5173   # React (dev) / 80 (prod)
Nginx:       localhost:80/443 # Proxy
Flower:      localhost:5555   # Monitor
```

---

## 📁 Estrutura de Arquivos

```
├── docker-compose.yml         ← Orquestração
├── .env                       ← Configurações (criar de .env.example)
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/                   ← Código será aqui
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── nginx.conf
│   └── src/                   ← Código React será aqui
│
├── nginx/
│   ├── conf.d/default.conf    ← Proxy config
│   └── ssl/                   ← Certificados
│
└── docker/
    ├── postgres/init.sql
    └── keycloak/init.sh
```

---

## 🔧 Troubleshooting Rápido

### Container não inicia
```bash
docker-compose logs backend  # Ver erro
docker-compose build --no-cache backend  # Rebuild
```

### Porta em uso
```bash
lsof -i :8000  # Ver o que está usando
# Editar .env e mudar a porta
```

### PostgreSQL falha
```bash
docker-compose down -v postgres
docker-compose up postgres
```

### Redis não conecta
```bash
docker-compose exec redis redis-cli -a redis_password_123 ping
# Deve responder: PONG
```

---

## ✅ Health Checks

```bash
# PostgreSQL
docker-compose exec postgres pg_isready -U laudos_user

# Redis
docker-compose exec redis redis-cli -a redis_password_123 ping

# Backend
curl http://localhost:8000/api/v1/health

# Frontend
curl http://localhost/

# Keycloak
curl http://localhost:8080/health/ready

# Todos os containers
docker-compose ps  # Procurar status "healthy"
```

---

## 📊 Volumes

```bash
# Ver volumes
docker volume ls | grep sistema_laudos

# Ver tamanho
docker system df

# Remover volumes
docker volume rm sistema_laudos_postgres_data

# Backup postgres
docker-compose exec postgres pg_dump -U laudos_user -d sistema_de_laudos > backup.sql

# Restore postgres
cat backup.sql | docker-compose exec -T postgres psql -U laudos_user -d sistema_de_laudos
```

---

## 🔍 Verificar Configurações

```bash
# Ver variáveis de ambiente no container
docker-compose exec backend env

# Ver arquivo de configuração
cat .env

# Validar docker-compose
docker-compose config

# Verificar conectividade entre containers
docker-compose exec backend ping redis
docker-compose exec backend curl http://postgres:5432
```

---

## 🛠️ Desenvolvimento

### Modo Hot Reload
```bash
# Backend (uvicorn detecta mudanças)
docker-compose up backend  # --reload está ativado no Dockerfile

# Frontend (Vite detecta mudanças)
docker-compose up frontend
```

### Parar um Serviço
```bash
docker-compose stop backend
docker-compose start backend
docker-compose restart backend
```

### Executar Migrations
```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic revision --autogenerate -m "Descricao"
```

### Instalar Novo Package Python
```bash
# Editar requirements.txt
docker-compose build --no-cache backend
docker-compose up backend
```

### Instalar Novo Package Node
```bash
# Editar package.json
docker-compose build --no-cache frontend
docker-compose up frontend
```

---

## 🚀 Deploy Verificação

Antes de commitar, rodar:

```bash
# Validar sintaxe
docker-compose config

# Build sem cache
docker-compose build --no-cache

# Todos containers healthy
docker-compose ps  # Procurar "healthy"

# Testes de conectividade
docker-compose exec backend curl http://localhost:8000/api/v1/health
curl http://localhost/
curl http://localhost:8000/docs
```

---

## 📝 Variáveis Importantes

```bash
# .env - Principais

# Banco
DB_NAME=sistema_de_laudos
DB_USER=laudos_user
DB_PASSWORD=laudos_password_123

# Redis
REDIS_PASSWORD=redis_password_123

# Backend
SECRET_KEY=sua_chave_secreta_aqui
DATABASE_URL=postgresql://laudos_user:laudos_password_123@postgres:5432/sistema_de_laudos

# Keycloak
KEYCLOAK_ADMIN_PASSWORD=keycloak_admin_123
KEYCLOAK_REALM=sistema_laudos

# Frontend
VITE_API_URL=http://localhost:8000/api
```

---

## 📞 Ajuda Rápida

```bash
# Limpar tudo (CUIDADO!)
docker system prune -a

# Ver consumo de recursos
docker stats

# Inspecionar container
docker inspect sistema_laudos_backend

# Logs de todos os containers
docker-compose logs --tail=50

# Limpeza
docker-compose exec redis redis-cli -a redis_password_123 FLUSHDB
docker-compose exec postgres psql -U laudos_user -d sistema_de_laudos -c "DROP SCHEMA laudos CASCADE;"
```

---

## 🎯 Próximas Fases

Depois de FASE 2 OK:

1. **FASE 3**: Banco de Dados com Alembic
2. **FASE 4**: Backend APIs
3. **FASE 5**: Frontend Components
4. **FASE 6**: Testes
5. **FASE 7**: Deploy

---

**Salve este arquivo para referência rápida! 🚀**

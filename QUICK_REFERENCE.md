# ⚡ Quick Reference Guide - Sistema de Laudos Docker Compose

## 🚀 Quick Start

```bash
cd /opt/app/sistema_de_laudos
docker compose --env-file .env.dev up -d
```

## ✅ Current Status (02/02/2026)

```
✅ Backend (FastAPI)      → http://localhost:8000
✅ Frontend (React)       → http://localhost:8080
✅ PostgreSQL 16          → localhost:5432
✅ Redis 7                → localhost:6379
✅ Nginx Proxy            → http://localhost:80
⚠️  Keycloak 25           → DISABLED (authentication issue)
```

---

## 📊 Common Commands

### View Status
```bash
docker compose --env-file .env.dev ps
```

### View Logs
```bash
# All services
docker compose --env-file .env.dev logs -f

# Specific service
docker compose --env-file .env.dev logs -f backend
docker compose --env-file .env.dev logs -f frontend
docker compose --env-file .env.dev logs -f postgres
docker compose --env-file .env.dev logs -f redis
docker compose --env-file .env.dev logs -f nginx
```

### Stop Everything
```bash
docker compose --env-file .env.dev down
```

### Stop & Clean Volumes
```bash
docker compose --env-file .env.dev down -v
```

### Restart Service
```bash
docker compose --env-file .env.dev restart backend
```

### Rebuild & Start
```bash
docker compose --env-file .env.dev up -d --build
```

---

## 🔌 Endpoints Available

| Service | URL | Purpose |
|---------|-----|---------|
| Backend | `http://localhost:8000` | FastAPI server |
| Backend Health | `http://localhost:8000/api/v1/health` | Health check |
| Frontend | `http://localhost:8080` | React app |
| Nginx | `http://localhost:80` | Reverse proxy |
| Nginx HTTPS | `https://localhost:443` | Secure proxy |
| PostgreSQL | `localhost:5432` | Database |
| Redis | `localhost:6379` | Cache/Queue |

---

## 🗄️ Database Access

### PostgreSQL Credentials
```
Host: localhost
Port: 5432
User: dbadmin_dev
Password: Dev@)((42))
Database: sistema_de_laudos_dev
```

### Connect via psql
```bash
psql -h localhost -U dbadmin_dev -d sistema_de_laudos_dev
```

### Connect via Docker
```bash
docker compose --env-file .env.dev exec postgres \
  psql -U dbadmin_dev -d sistema_de_laudos_dev
```

---

## 💾 Redis Access

### Redis Credentials
```
Host: localhost
Port: 6379
Password: redisadmin_dev
```

### Connect via Redis CLI
```bash
docker compose --env-file .env.dev exec redis \
  redis-cli -a redisadmin_dev
```

---

## 🧪 Testing

### Test Backend Health
```bash
curl http://localhost:8000/api/v1/health
```

### Expected Response
```json
{
  "status": "healthy",
  "service": "Sistema de Laudos Backend",
  "version": "1.0.0"
}
```

### Test Nginx
```bash
curl http://localhost:80
```

---

## 📈 Performance Metrics

```bash
# View resource usage
docker stats --no-stream
```

**Current Usage:**
- CPU: ~0.53% (excellent)
- Memory: ~65 MB (0.83% of available)

---

## 🔍 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker compose --env-file .env.dev logs SERVICE_NAME

# Restart service
docker compose --env-file .env.dev restart SERVICE_NAME

# Full restart
docker compose --env-file .env.dev down
docker compose --env-file .env.dev up -d
```

### Port Already in Use
```bash
# Find process using port
lsof -i :PORT_NUMBER

# Kill process
kill -9 PID
```

### Database Connection Issues
```bash
# Test connection
docker compose --env-file .env.dev exec postgres pg_isready
```

### Clear All Data
```bash
docker compose --env-file .env.dev down -v
docker compose --env-file .env.dev up -d
```

---

## ⚠️ Known Issues

### Keycloak (Disabled)
- **Status:** Not running (intentionally disabled)
- **Reason:** PostgreSQL authentication issue
- **Workaround:** Placeholder database created
- **To Fix:** Use simpler password without special characters

---

## 📁 Important Files

- `docker-compose.yml` - Service definitions
- `.env.dev` - Environment variables
- `docker/postgres/init.sql` - DB initialization
- `nginx/nginx.conf` - Proxy configuration
- `frontend/Dockerfile` - React build
- `backend/Dockerfile` - FastAPI build

---

## 📚 Documentation

- [ANALISE_FINAL_DOCKER_COMPOSE.md](ANALISE_FINAL_DOCKER_COMPOSE.md) - Complete analysis
- [TROUBLESHOOTING_LOG.md](TROUBLESHOOTING_LOG.md) - Issues & solutions
- [DOCKER_EXECUTION_SUMMARY.md](DOCKER_EXECUTION_SUMMARY.md) - Executive summary

---

## 🔐 Security Notes

### Development Environment
- ⚠️ DEBUG=true (disable in production)
- ⚠️ LOG_LEVEL=DEBUG (reduce in production)
- ⚠️ Passwords visible in .env file
- ⚠️ Self-signed SSL certificates

### Production Checklist
- [ ] Change all passwords
- [ ] Set DEBUG=false
- [ ] Generate proper SSL certificates
- [ ] Configure CORS properly
- [ ] Set up authentication (Keycloak/OAuth)
- [ ] Enable HTTPS only
- [ ] Setup log aggregation
- [ ] Configure monitoring

---

## 🎯 Next Steps

1. **Verify all endpoints** are responding
2. **Test database connectivity** from backend
3. **Check Redis caching** is working
4. **Fix Keycloak** if needed
5. **Deploy to staging** for integration testing

---

**Last Updated:** 02/02/2026 20:25 UTC  
**Status:** ✅ OPERATIONAL (5/6 services)

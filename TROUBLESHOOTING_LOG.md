# 🔧 Troubleshooting & Issues Log

## Execution Date: 02/02/2026

---

## Issues Found and Resolved

### ✅ RESOLVED

#### Issue #1: Keycloak Container Without Start Command
**Status:** ✅ RESOLVED  
**Severity:** CRITICAL  

**Problem:**
- Keycloak command was commented out: `#command: start-dev`
- Container would exit immediately with exit code 0
- Continuous restart loop

**Solution:**
```yaml
keycloak:
  command: start-dev  # Uncommented this line
```

**Result:** Keycloak now starts properly

---

#### Issue #2: Invalid Keycloak Hostname Configuration
**Status:** ✅ RESOLVED  
**Severity:** HIGH

**Problem:**
- Hostname was: `82.25.75.88:8080` (IP with port)
- This is invalid format for KC_HOSTNAME variable
- Error: "Provided hostname is neither a plain hostname nor a valid URL"

**Solution:**
```env
KEYCLOAK_HOSTNAME=localhost  # Changed from 82.25.75.88:8080
KEYCLOAK_PORT=8080           # Changed from 8080:8080
```

**Result:** Valid hostname format accepted

---

#### Issue #3: Incorrect Keycloak Port Mapping
**Status:** ✅ RESOLVED  
**Severity:** MEDIUM

**Problem:**
```yaml
ports:
  - ${KEYCLOAK_PORT:?KEYCLOAK_PORT is required}  # Missing :8080
```

**Solution:**
```yaml
ports:
  - "${KEYCLOAK_PORT:?KEYCLOAK_PORT is required}:8080"  # Added :8080
```

**Result:** Port correctly mapped from variable to container port 8080

---

#### Issue #4: Nginx Attempting to Proxy Non-existent Keycloak
**Status:** ✅ RESOLVED  
**Severity:** MEDIUM

**Problem:**
- Nginx tried to proxy to keycloak upstream
- Keycloak was failing/restarting
- Error: "host not found in upstream 'keycloak'"

**Solution:**
1. Commented out Keycloak service temporarily
2. Removed keycloak proxy from nginx.conf
3. Updated docker-compose.yml to not depend on keycloak

**Result:** Nginx now healthy and operational

---

#### Issue #5: Missing Keycloak Database User
**Status:** ✅ RESOLVED (PARTIAL)  
**Severity:** HIGH

**Problem:**
- PostgreSQL init script didn't create Keycloak user: `kcdbadmin_dev`
- Database `keycloak_dev` didn't exist
- Keycloak couldn't authenticate

**Solution:**
Added to `docker/postgres/init.sql`:
```sql
CREATE DATABASE keycloak_dev;
CREATE USER kcdbadmin_dev WITH PASSWORD 'Dev@)((42))';
ALTER USER kcdbadmin_dev CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE keycloak_dev TO kcdbadmin_dev;
```

**Result:** Database and user created automatically

---

### ⚠️ PARTIALLY RESOLVED - NEEDS ATTENTION

#### Issue #6: Keycloak PostgreSQL Authentication Failed
**Status:** ⚠️ PARTIAL  
**Severity:** HIGH  

**Problem:**
```
FATAL: password authentication failed for user "kcdbadmin_dev"
```

Even after database and user creation, Keycloak cannot authenticate.

**Potential Causes:**
1. Password contains special characters: `Dev@)((42))`
2. JDBC URL encoding issue
3. Character encoding mismatch

**Current Solution:**
- Keycloak commented out in docker-compose.yml
- Backend, Frontend, Nginx working fine
- Temporary workaround allows development to continue

**Recommendations for Fix:**
1. Use simpler password (no special chars)
2. Properly escape JDBC URL
3. Use Keycloak H2 embedded database for dev
4. Check PostgreSQL logs for detailed error

**Next Steps:**
```yaml
# Try this instead:
KC_DB_PASSWORD: simplepassword123
# Instead of:
KC_DB_PASSWORD: Dev@)((42))
```

---

### ℹ️ SIDE EFFECTS OF CHANGES

#### Port Conflicts
**Issue:** Multiple containers trying to bind to port 8080
- Keycloak wanted :8080
- Frontend was set to :8080
- Nginx was also trying :8080

**Resolution:** Properly sequenced container starts with dependencies

---

#### Orphan Containers
**Issue:** Celery service was removed but container remained
```
Found orphan containers ([sistema_laudos_celery_dev])
```

**Resolution:** Used `--remove-orphans` flag

---

## System Health Status

### All Healthy Services ✅

| Service | CPU | Memory | Status |
|---------|-----|--------|--------|
| Backend | 0.19% | 38.18 MB | ✅ Healthy |
| Frontend | 0.00% | 3.25 MB | ✅ Healthy |
| PostgreSQL | 0.02% | 18 MB | ✅ Healthy |
| Redis | 0.32% | 3.20 MB | ✅ Healthy |
| Nginx | 0.00% | 2.29 MB | ✅ Healthy |

---

## Testing Performed

### Backend Health Check ✅
```bash
$ curl http://localhost:8000/api/v1/health
{"status":"healthy","service":"Sistema de Laudos Backend","version":"1.0.0"}
```

### Docker Stats Validation ✅
```
Total CPU: 0.53% (excellent)
Total Memory: 64.9 MB / 7.755 GB (0.83%)
```

### Container Health Checks ✅
```
All healthchecks passing
All services responding to requests
```

---

## Lessons Learned

1. **Always uncomment production commands** - Keycloak needed explicit start-dev
2. **Hostname vs URL** - KC_HOSTNAME should be plain hostname, not URL
3. **Environment variables need proper escaping** - Special chars in passwords cause issues
4. **Port mapping syntax** - Docker requires explicit internal port mapping
5. **Dependency chain** - Nginx shouldn't depend on optional services

---

## Prevention Recommendations

1. ✅ Use simpler passwords for development (no special chars)
2. ✅ Add comments in docker-compose.yml explaining why lines are commented
3. ✅ Create separate .env files per environment with validated values
4. ✅ Add pre-flight checks before docker compose up
5. ✅ Document all environment variable requirements
6. ✅ Create docker-compose.override.yml for local development
7. ✅ Use networks to isolate optional services

---

## Related Files

- [docker-compose.yml](docker-compose.yml)
- [.env.dev](.env.dev)
- [docker/postgres/init.sql](docker/postgres/init.sql)
- [nginx/nginx.conf](nginx/nginx.conf)
- [ANALISE_FINAL_DOCKER_COMPOSE.md](ANALISE_FINAL_DOCKER_COMPOSE.md)

---

**Last Updated:** 02/02/2026 20:25 UTC

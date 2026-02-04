# 🚀 RATE LIMITING - QUICK REFERENCE

**File**: [app/api/rate_limiting.py](../backend/app/api/rate_limiting.py)  
**Status**: ✅ Production Ready  
**Last Updated**: 2024-02-03  

---

## 📊 Rate Limit Matrix

| Endpoint | Method | Path | Limit | Key Use Case |
|----------|--------|------|-------|--------------|
| **upload_contrato** | POST | `/api/v1/contratos/upload` | 10/min | File uploads (expensive) |
| **list_contratos** | GET | `/api/v1/contratos` | 50/min | Read operation |
| **get_contrato** | GET | `/api/v1/contratos/{id}` | 50/min | Single read |
| **delete_contrato** | DELETE | `/api/v1/contratos/{id}` | 10/min | Destructive operation |
| **list_pareceres** | GET | `/api/v1/pareceres` | 50/min | Read operation |
| **get_parecer** | GET | `/api/v1/pareceres/{id}` | 50/min | Single read |
| **delete_parecer** | DELETE | `/api/v1/pareceres/{id}` | 10/min | Destructive operation |
| **list_bureau** | GET | `/api/v1/bureau` | 50/min | Read operation |
| **get_bureau** | GET | `/api/v1/bureau/{id}` | 50/min | Single read |
| **analisar_geolocalizacao** | POST | `/api/v1/geolocalizacao/analisar` | 10/min | Geolocation analysis |
| **get_geolocalizacao** | GET | `/api/v1/geolocalizacao/{id}` | 50/min | Read operation |
| **get_my_activity** | GET | `/api/v1/audit-logs/my-activity` | 20/min | Personal audit queries |
| **get_tenant_activity** | GET | `/api/v1/audit-logs/tenant-activity` | 5/min | Sensitive admin queries |
| **get_resource_history** | GET | `/api/v1/audit-logs/resource/{type}/{id}` | 20/min | Audit history |
| **get_failed_actions** | GET | `/api/v1/audit-logs/failed-actions` | 5/min | Security monitoring |
| **get_activity_summary** | GET | `/api/v1/audit-logs/activity-summary` | 5/min | Sensitive statistics |
| **detect_suspicious_activity** | GET | `/api/v1/audit-logs/suspicious-activity` | 5/min | Security monitoring |
| **health_check** | GET | `/api/v1/health` | ∞ | No limit (monitoring) |

---

## 🔧 Configuration

### RateLimits Class

```python
from app.api.rate_limiting import RateLimits

class RateLimits:
    UPLOAD = "10/minute"      # File uploads, expensive operations
    DELETE = "10/minute"      # Destructive operations
    WRITE = "20/minute"       # POST, PUT, PATCH
    READ = "50/minute"        # GET endpoints
    UNLIMITED = None          # No rate limit
    AUDIT = "20/minute"       # Audit log queries
    ADMIN = "5/minute"        # Admin-only operations
    AUTH = "5/minute"         # Login/auth endpoints
```

---

## 💻 Usage Examples

### Basic Decorator Usage

```python
from fastapi import APIRouter, Request
from app.api.rate_limiting import limiter, RateLimits

router = APIRouter()

@router.get("/data")
@limiter.limit(RateLimits.READ)  # 50 requests per minute
async def get_data(request: Request):
    """Get data endpoint with rate limiting."""
    return {"data": "example"}
```

### With Authentication

```python
from app.api.decorators import require_tenant, require_roles
from app.api.dependencies import get_identity
from app.core.oidc_models import Identity

@router.get("/admin-data")
@require_tenant()
@require_roles("admin")
@limiter.limit(RateLimits.ADMIN)  # 5 requests per minute
async def get_admin_data(
    request: Request,  # ← REQUIRED for rate limiting
    identity: Identity = Depends(get_identity)
):
    """Admin-only endpoint with rate limiting."""
    return {"admin_data": "secret"}
```

### Custom Limit

```python
@router.post("/expensive-operation")
@limiter.limit("5/hour")  # Custom limit
async def expensive_operation(request: Request):
    """Custom rate limit (5 per hour)."""
    return {"status": "processed"}
```

---

## 📍 Key Points

### ✅ DO:

- ✅ Include `request: Request` parameter
- ✅ Add `@limiter.limit()` decorator after auth decorators
- ✅ Document rate limit in docstring
- ✅ Add 429 response to OpenAPI schema
- ✅ Use `RateLimits.XXX` constants

### ❌ DON'T:

- ❌ Forget the `request` parameter
- ❌ Put rate limit decorator before auth/roles
- ❌ Use bare strings like `"10/minute"` (use constants)
- ❌ Rate limit health check endpoints
- ❌ Mix rate limiting approaches

---

## 🧪 Testing Rate Limits

### Using curl

```bash
# Test with rapid requests
for i in {1..15}; do
  curl -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/v1/contratos
  sleep 0.1
done

# After 50 requests in a minute:
# HTTP/1.1 429 Too Many Requests
# Retry-After: 60
```

### Using Python requests

```python
import requests
import time

def test_rate_limit(endpoint, token, limit_per_min=50):
    """Test rate limiting by making rapid requests."""
    headers = {"Authorization": f"Bearer {token}"}
    
    for i in range(limit_per_min + 5):
        response = requests.get(
            f"http://localhost:8000/api/v1{endpoint}",
            headers=headers
        )
        
        if response.status_code == 429:
            print(f"✓ Rate limited after {i} requests")
            print(f"  Retry-After: {response.headers.get('Retry-After')}")
            return
        
        print(f"  Request {i+1}: {response.status_code}")
```

### Using Python asyncio

```python
import asyncio
import httpx

async def test_rate_limit_async(endpoint, token):
    """Test rate limiting with async requests."""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        for i in range(55):
            response = await client.get(
                f"http://localhost:8000/api/v1{endpoint}",
                headers=headers
            )
            
            if response.status_code == 429:
                print(f"Rate limited after {i} requests")
                break
            
            print(f"Request {i+1}: {response.status_code}")
```

---

## 🔍 Monitoring Rate Limit Hits

### Check Audit Logs

Failed rate-limited requests are captured in audit logs:

```bash
# View failed actions in admin panel
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/audit-logs/failed-actions

# Check suspicious activity
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/audit-logs/suspicious-activity?threshold=20
```

### Logs to Look For

```
# In app logs:
[WARNING] Rate limit exceeded for IP: 192.168.1.100
[WARNING] Rate limit exceeded for user: user@example.com
[WARNING] Suspicious activity detected: IP with 25 failed requests in 24h
```

---

## ⚙️ Configuration for Production

### Option 1: Using Redis (Distributed)

For multi-instance deployments:

```bash
pip install slowapi[redis]
```

```python
# app/api/rate_limiting.py
from slowapi.util import get_remote_address
from slowapi import Limiter
import slowapi.ext.storage

# Use Redis storage for distributed rate limiting
storage = slowapi.ext.storage.RedisStorage("redis://localhost:6379")
limiter = Limiter(
    key_func=get_remote_address,
    storage_backend=storage,
)
```

### Option 2: Adjust Limits by Environment

```python
# app/api/rate_limiting.py
import os

ENV = os.getenv("ENVIRONMENT", "development")

class RateLimits:
    if ENV == "production":
        UPLOAD = "5/minute"   # Stricter in production
        DELETE = "5/minute"
        READ = "100/minute"
        ADMIN = "2/minute"
    else:
        UPLOAD = "100/minute"  # Lenient in development
        DELETE = "100/minute"
        READ = "1000/minute"
        ADMIN = "500/minute"
```

### Option 3: Per-User Rate Limiting

```python
from slowapi.util import get_remote_address

def get_user_key(request):
    """Rate limit by authenticated user instead of IP."""
    user_id = request.state.user_id  # Set by auth middleware
    if user_id:
        return user_id
    return get_remote_address(request)

limiter = Limiter(key_func=get_user_key)
```

---

## 📚 References

- **slowapi Documentation**: https://slowapi.readthedocs.io/
- **FastAPI Rate Limiting**: https://fastapi.tiangolo.com/
- **HTTP 429 Status**: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429

---

## 🎯 Next Steps

- [ ] Monitor rate limit hits in production
- [ ] Adjust limits based on actual usage patterns
- [ ] Consider implementing Redis for distributed rate limiting
- [ ] Add rate limiting dashboard/monitoring
- [ ] Document rate limits in API documentation

---

**Last Updated**: 2024-02-03  
**Maintained By**: Sistema de Laudos Team  
**Status**: ✅ Production Ready  

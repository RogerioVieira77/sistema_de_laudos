# 🔐 KEYCLOAK - QUICK REFERENCE FOR FRONTEND

**Last Updated**: 2025-02-03  
**Environment**: Development

---

## 🎯 Essential Info

```env
VITE_KEYCLOAK_URL=http://localhost:8081
VITE_KEYCLOAK_REALM=sistema_laudos_dev
VITE_KEYCLOAK_CLIENT_ID=sistema_laudos_backend_dev
VITE_KEYCLOAK_CLIENT_SECRET=frTqxpABgXCkikANferUADHYqlmrReYW
```

**Admin Access**: kcadmin_dev / Dev@)((42))

---

## 🧪 Test Credentials

| User | Email | Password | Role |
|------|-------|----------|------|
| Admin | admin@test.com | Password@123 | admin |
| Analyst | analyst@test.com | Password@123 | analyst |
| Regular | user@test.com | Password@123 | user |

---

## 📡 API Endpoints

**Token (Password Grant)**:
```
POST http://localhost:8081/realms/sistema_laudos_dev/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded

client_id=sistema_laudos_backend_dev
client_secret=frTqxpABgXCkikANferUADHYqlmrReYW
username=admin
password=Password@123
grant_type=password
```

**UserInfo**:
```
GET http://localhost:8081/realms/sistema_laudos_dev/protocol/openid-connect/userinfo
Authorization: Bearer <access_token>
```

**Logout**:
```
POST http://localhost:8081/realms/sistema_laudos_dev/protocol/openid-connect/logout
```

---

## 🔌 Frontend Setup Checklist

- [ ] `npm install oidc-client-ts`
- [ ] Create `src/contexts/AuthContext.jsx`
- [ ] Create `src/components/Login.jsx`
- [ ] Create `src/components/ProtectedRoute.jsx`
- [ ] Add Keycloak env vars to `.env.dev`
- [ ] Initialize OIDC client in App startup
- [ ] Implement token refresh logic
- [ ] Test login flow with all 3 users
- [ ] Validate role-based access
- [ ] Test logout flow

---

## ⚡ Quick Test

### Get Token
```bash
curl -X POST http://localhost:8081/realms/sistema_laudos_dev/protocol/openid-connect/token \
  -d "client_id=sistema_laudos_backend_dev" \
  -d "client_secret=frTqxpABgXCkikANferUADHYqlmrReYW" \
  -d "username=admin" \
  -d "password=Password@123" \
  -d "grant_type=password" | jq '.access_token'
```

### Decode Token (paste in https://jwt.io)
The JWT contains:
- `sub`: User ID
- `preferred_username`: Username
- `email`: Email address
- `realm_access.roles`: Array of roles

---

## 🚨 Troubleshooting

**Invalid Credentials?**
→ Verify password is exactly: `Password@123`

**CORS Error?**
→ Check redirect_uris in Keycloak client are correct

**Token Expired?**
→ Implement refresh token flow in frontend

**Access Denied?**
→ Verify user role matches required role

---

## 📚 Next: PASSO 3

See: [PASSO_3_FRONTEND_OIDC.md](./PASSO_3_FRONTEND_OIDC.md)

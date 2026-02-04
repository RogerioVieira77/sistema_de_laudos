# 🛡️ POLÍTICAS DE SEGURANÇA POR ENDPOINT

**Data:** 2024-02-03  
**Versão:** 1.0  
**Aplicável:** Todos endpoints da API

---

## 📋 ESTRUTURA DE ROLES

```
┌──────────────────────────────────────────────────────────┐
│                    HIERARQUIA DE ROLES                   │
└──────────────────────────────────────────────────────────┘

admin
├─ Todos endpoints
├─ Todos dados
├─ Gestão de usuários
└─ Auditoria completa

revisor
├─ Criar parecer/análise
├─ Ver todos laudos
├─ Revisar documentos
├─ Exportar relatórios
└─ NÃO pode deletar

analista
├─ Upload de contrato
├─ Processar laudos
├─ Ver geolocalização
├─ Gerar parecer
└─ NÃO pode revisar

visualizador
├─ VER laudos (read-only)
├─ Baixar documentos
├─ VER relatórios
└─ NÃO pode criar/editar
```

---

## 🔒 MATRIZ DE ACESSO POR ENDPOINT

### **CONTRATOS** 📄

#### `POST /api/v1/contratos` - Upload de contrato

```
Método: POST
Caminho: /api/v1/contratos
Payload:
{
  "file": "arquivo.pdf",
  "metadata": {
    "client_name": "string",
    "contract_type": "string"
  }
}

┌─────────────────────────────────────────────┐
│ SEGURANÇA                                   │
├─────────────────────────────────────────────┤
│ Autenticação: ✅ Obrigatória                │
│ Roles:        analista, revisor, admin      │
│ Rate Limit:   10/minuto por usuário         │
│ File Size:    Max 50MB                      │
│ File Type:    application/pdf               │
│ CORS:         https://*.empresa.com         │
│ Audit:        ✅ Log de upload              │
└─────────────────────────────────────────────┘

Response 201:
{
  "id": "uuid",
  "filename": "contrato_20240203.pdf",
  "size_bytes": 1500000,
  "uploaded_by": "user_id",
  "uploaded_at": "2024-02-03T10:30:00Z",
  "status": "processing",
  "tenant_id": "tenant-123"
}

Errors:
- 400: Arquivo inválido
- 401: Não autenticado
- 403: Role insuficiente
- 413: Arquivo muito grande
- 429: Rate limit excedido
```

---

#### `GET /api/v1/contratos` - Listar contratos

```
Método: GET
Caminho: /api/v1/contratos
Query Params:
  ?page=1&limit=20&sort_by=created_at&sort_order=desc
  &status=processing,completed
  &search=contrato

┌─────────────────────────────────────────────┐
│ SEGURANÇA                                   │
├─────────────────────────────────────────────┤
│ Autenticação: ✅ Obrigatória                │
│ Roles:        visualizador+                 │
│               (analista, revisor, admin)    │
│ Rate Limit:   100/minuto por usuário        │
│ Tenant:       ✅ Filtro automático          │
│ Audit:        ⚠️ Apenas estatístico         │
└─────────────────────────────────────────────┘

Lógica Backend:
```python
@router.get("/contratos")
def listar_contratos(
    page: int = 1,
    limit: int = 20,
    identity=Depends(get_identity)
):
    # 1. Validar range
    assert 1 <= page, "page >= 1"
    assert 1 <= limit <= 100, "limit 1-100"
    
    # 2. Filtrar por tenant (obrigatório!)
    contratos = db.query(Contrato)\
        .filter_by(tenant_id=identity.tenant_id)\
        .filter_by(status__in=["processing", "completed"])\
        .paginate(page, limit)
    
    # 3. Responder
    return {"data": contratos, "total": total}
```

**Response 200:**
```json
{
  "data": [
    {
      "id": "uuid",
      "filename": "contrato.pdf",
      "status": "completed",
      "created_at": "2024-02-03T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150
  }
}
```

---

#### `GET /api/v1/contratos/{id}` - Detalhes de um contrato

```
Método: GET
Caminho: /api/v1/contratos/{id}

┌─────────────────────────────────────────────┐
│ SEGURANÇA                                   │
├─────────────────────────────────────────────┤
│ Autenticação: ✅ Obrigatória                │
│ Roles:        visualizador+                 │
│ Rate Limit:   100/minuto                    │
│ Tenant:       ✅ Validação                  │
│ Audit:        ⚠️ Apenas GET (read-only)     │
└─────────────────────────────────────────────┘

```python
@router.get("/contratos/{id}")
def get_contrato(
    id: str,
    identity=Depends(get_identity)
):
    contrato = db.get(id)
    
    # ✅ CRÍTICO: Validar tenant
    if contrato.tenant_id != identity.tenant_id:
        raise HTTPException(403, "Acesso negado")
    
    return contrato
```

---

#### `DELETE /api/v1/contratos/{id}` - Deletar contrato

```
Método: DELETE
Caminho: /api/v1/contratos/{id}

┌─────────────────────────────────────────────┐
│ SEGURANÇA                                   │
├─────────────────────────────────────────────┤
│ Autenticação: ✅ Obrigatória                │
│ Roles:        admin APENAS                  │
│ Rate Limit:   5/minuto                      │
│ Tenant:       ✅ Validação                  │
│ Audit:        ✅ Log DELETE                 │
│ Soft Delete:  ✅ (não apaga, marca deleted) │
└─────────────────────────────────────────────┘

```python
@router.delete("/contratos/{id}")
def delete_contrato(
    id: str,
    identity=Depends(require_roles("admin"))
):
    contrato = db.get(id)
    
    # Validar tenant
    if contrato.tenant_id != identity.tenant_id:
        raise HTTPException(403, "Acesso negado")
    
    # Soft delete (marcar como deleted)
    contrato.deleted_at = datetime.utcnow()
    contrato.deleted_by = identity.user_id
    db.save(contrato)
    
    # Log audit
    await log_audit(
        user_id=identity.user_id,
        action="DELETE",
        resource="contrato",
        resource_id=id,
        status="SUCCESS",
        tenant_id=identity.tenant_id
    )
    
    return {"message": "Deletado com sucesso"}
```

---

### **GEOLOCALIZAÇÃO** 🗺️

#### `GET /api/v1/contratos/{id}/locations` - Locais do contrato

```
Método: GET
Caminho: /api/v1/contratos/{id}/locations

┌─────────────────────────────────────────────┐
│ SEGURANÇA                                   │
├─────────────────────────────────────────────┤
│ Autenticação: ✅ Obrigatória                │
│ Roles:        visualizador+                 │
│ Rate Limit:   200/minuto                    │
│ Tenant:       ✅ Validação                  │
│ Cache:        ✅ 5 minutos                  │
│ Audit:        ⚠️ Opcional                   │
└─────────────────────────────────────────────┘
```

---

#### `POST /api/v1/locations/distance` - Calcular distância

```
Método: POST
Caminho: /api/v1/locations/distance
Payload:
{
  "from": {
    "latitude": -15.7975,
    "longitude": -47.8919
  },
  "to": {
    "latitude": -23.5505,
    "longitude": -46.6333
  }
}

┌─────────────────────────────────────────────┐
│ SEGURANÇA                                   │
├─────────────────────────────────────────────┤
│ Autenticação: ✅ Obrigatória                │
│ Roles:        visualizador+                 │
│ Rate Limit:   500/minuto (alto - cálculo)  │
│ Tenant:       ⚠️ Não aplicável (geoloc)    │
│ Audit:        ❌ Não necessário             │
│ Input Valid:  ✅ Lat/Long ranges            │
└─────────────────────────────────────────────┘

Validações:
```python
def validate_coordinates(lat, lon):
    assert -90 <= lat <= 90, "Latitude inválida"
    assert -180 <= lon <= 180, "Longitude inválida"
```

---

### **PARECER (Análise Legal)** ⚖️

#### `POST /api/v1/parecer` - Gerar parecer

```
Método: POST
Caminho: /api/v1/parecer
Payload:
{
  "contrato_id": "uuid",
  "analysis_type": "full|quick",
  "include_sections": ["legal", "compliance", "risk"]
}

┌─────────────────────────────────────────────┐
│ SEGURANÇA                                   │
├─────────────────────────────────────────────┤
│ Autenticação: ✅ Obrigatória                │
│ Roles:        analista, revisor, admin      │
│ Rate Limit:   5/minuto (processamento caro) │
│ Tenant:       ✅ Validação (contrato)       │
│ Audit:        ✅ Log CRIAR parecer          │
│ Async:        ✅ Job em background          │
└─────────────────────────────────────────────┘

```python
@router.post("/parecer")
async def criar_parecer(
    req: PareceCreateRequest,
    identity=Depends(require_roles("analista", "revisor", "admin"))
):
    # 1. Validar contrato existe e pertence ao tenant
    contrato = db.get(Contrato, req.contrato_id)
    if not contrato or contrato.tenant_id != identity.tenant_id:
        raise HTTPException(404, "Contrato não encontrado")
    
    # 2. Audit antes de iniciar
    await log_audit(
        user_id=identity.user_id,
        action="CREATE",
        resource="parecer",
        resource_id=req.contrato_id,
        status="PENDING",
        details={"analysis_type": req.analysis_type},
        tenant_id=identity.tenant_id
    )
    
    # 3. Enfileirar job async
    job_id = await background_jobs.queue(
        "generate_parecer",
        {
            "contrato_id": req.contrato_id,
            "analysis_type": req.analysis_type,
            "user_id": identity.user_id,
            "tenant_id": identity.tenant_id
        }
    )
    
    # 4. Retornar job_id para polling
    return {"job_id": job_id, "status": "processing"}
```

---

#### `GET /api/v1/parecer/{id}` - Detalhes do parecer

```
Método: GET
Caminho: /api/v1/parecer/{id}

┌─────────────────────────────────────────────┐
│ SEGURANÇA                                   │
├─────────────────────────────────────────────┤
│ Autenticação: ✅ Obrigatória                │
│ Roles:        visualizador+                 │
│ Rate Limit:   100/minuto                    │
│ Tenant:       ✅ Validação                  │
│ Sensitive:    ⚠️ Pode ter dados PII         │
│ Audit:        ⚠️ Access log (PII)           │
└─────────────────────────────────────────────┘
```

---

#### `GET /api/v1/parecer/{id}/pdf` - Download PDF

```
Método: GET
Caminho: /api/v1/parecer/{id}/pdf
Query: ?token=signed_download_token

┌─────────────────────────────────────────────┐
│ SEGURANÇA                                   │
├─────────────────────────────────────────────┤
│ Autenticação: ✅ Obrigatória (via token)    │
│ Roles:        visualizador+                 │
│ Rate Limit:   20/minuto (downloads caros)   │
│ Tenant:       ✅ Validação                  │
│ Expiry:       ✅ Token 1 hora               │
│ Virus Check:  ✅ Scan before download       │
│ Audit:        ✅ Log DOWNLOAD (PII)         │
│ HTTPS:        ✅ Obrigatório                │
└─────────────────────────────────────────────┘

Implementação:
```python
@router.get("/parecer/{id}/pdf")
async def download_parecer_pdf(
    id: str,
    token: str = Query(...),
    identity=Depends(get_identity)
):
    # 1. Validar token de download
    try:
        download_claim = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        # Token deve referenciar este resource
        assert download_claim["sub"] == identity.user_id
        assert download_claim["resource"] == id
        assert download_claim["exp"] > time.time()
    except:
        raise HTTPException(403, "Download link expirado ou inválido")
    
    # 2. Validar parecer
    parecer = db.get(Parecer, id)
    if not parecer or parecer.tenant_id != identity.tenant_id:
        raise HTTPException(404)
    
    # 3. Audit
    await log_audit(
        user_id=identity.user_id,
        action="DOWNLOAD",
        resource="parecer",
        resource_id=id,
        status="SUCCESS",
        details={"file_size": parecer.pdf_size},
        tenant_id=identity.tenant_id
    )
    
    # 4. Responder com PDF
    return FileResponse(
        parecer.pdf_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{parecer.filename}"'}
    )
```

---

### **BUREAU (Dados de Crédito)** 💰

#### `GET /api/v1/bureau/{contrato_id}` - Consultar dados de crédito

```
Método: GET
Caminho: /api/v1/bureau/{contrato_id}

┌─────────────────────────────────────────────┐
│ SEGURANÇA (CRÍTICO - Dados PII/Sensíveis)   │
├─────────────────────────────────────────────┤
│ Autenticação: ✅ Obrigatória                │
│ Roles:        analista, revisor, admin ONLY │
│ Rate Limit:   50/minuto (dados sensíveis)   │
│ Tenant:       ✅ Validação                  │
│ Encryption:   ✅ TLS 1.3+ obrigatório       │
│ Audit:        ✅ Log COMPLETO (quem, quando)│
│ Masking:      ⚠️ CPF/CNPJ parcialmente      │
│ Retention:    ✅ 6 meses (LGPD compliance) │
│ Access Log:   ✅ Alertas de acesso inusual  │
└─────────────────────────────────────────────┘

Response (CPF mascarado):
```json
{
  "cpf": "123.456.***-**",
  "score": 750,
  "risk_level": "low",
  "restrictions": [
    {
      "type": "serasa",
      "amount": 5000.00,
      "date": "2023-06-15"
    }
  ],
  "accessed_at": "2024-02-03T10:30:00Z",
  "accessed_by": "user_id"
}
```

```python
def mask_cpf(cpf: str) -> str:
    """Mascarar CPF mantendo últimos 2 dígitos visíveis"""
    # 123.456.789-10 → 123.456.***-**
    clean = cpf.replace(".", "").replace("-", "")
    return f"{clean[:3]}.{clean[3:6]}.***-**"

@router.get("/bureau/{contrato_id}")
async def consultar_bureau(
    contrato_id: str,
    identity=Depends(require_roles("analista", "revisor", "admin"))
):
    contrato = db.get(Contrato, contrato_id)
    if not contrato or contrato.tenant_id != identity.tenant_id:
        raise HTTPException(404)
    
    # Buscar dados bureau (pode ser terceiro)
    bureau_data = await bureau_service.fetch(contrato.cpf)
    
    # Mascarar PII
    bureau_data["cpf"] = mask_cpf(bureau_data["cpf"])
    
    # Audit
    await log_audit(
        user_id=identity.user_id,
        action="VIEW",
        resource="bureau",
        resource_id=contrato_id,
        status="SUCCESS",
        details={"score_access": True},
        tenant_id=identity.tenant_id
    )
    
    return bureau_data
```

---

#### `POST /api/v1/bureau/{id}/export` - Exportar relatório

```
Método: POST
Caminho: /api/v1/bureau/{id}/export
Payload:
{
  "format": "pdf|csv",
  "include_sensitive": false
}

┌─────────────────────────────────────────────┐
│ SEGURANÇA (CRÍTICO - Exportação de dados)   │
├─────────────────────────────────────────────┤
│ Autenticação: ✅ Obrigatória                │
│ Roles:        revisor, admin ONLY           │
│ Rate Limit:   5/minuto (muito restritivo)   │
│ Tenant:       ✅ Validação                  │
│ Audit:        ✅ Log COMPLETO (exportação)  │
│ Sensitive:    ✅ Nunca exportar sem maskear │
│ Encryption:   ✅ Arquivo encriptado         │
│ Retention:    ✅ 7 dias depois auto-delete  │
│ Access Log:   ✅ Alertas (quem exportou)    │
└─────────────────────────────────────────────┘

```python
@router.post("/bureau/{id}/export")
async def export_bureau(
    id: str,
    req: ExportRequest,
    identity=Depends(require_roles("revisor", "admin"))
):
    bureau = db.get(Bureau, id)
    
    # 1. Validar acesso
    if bureau.tenant_id != identity.tenant_id:
        raise HTTPException(403)
    
    # 2. Gerar arquivo
    if req.format == "pdf":
        file_data = await pdf_service.generate_bureau_report(
            bureau,
            include_sensitive=req.include_sensitive and identity.is_admin()
        )
    
    # 3. Encriptar arquivo
    encrypted_data = encrypt(file_data, settings.EXPORT_KEY)
    
    # 4. Salvar temporariamente (7 dias)
    export_id = str(uuid4())
    storage.save(
        f"exports/{export_id}.zip",
        encrypted_data,
        ttl=7*24*60*60  # 7 dias
    )
    
    # 5. Audit (CRÍTICO)
    await log_audit(
        user_id=identity.user_id,
        action="EXPORT",
        resource="bureau",
        resource_id=id,
        status="SUCCESS",
        details={
            "format": req.format,
            "include_sensitive": req.include_sensitive,
            "export_id": export_id,
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent")
        },
        tenant_id=identity.tenant_id
    )
    
    # 6. Criar download link assinado
    download_token = jwt.encode(
        {
            "export_id": export_id,
            "user_id": identity.user_id,
            "exp": int(time.time()) + 3600  # 1 hora
        },
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    return {
        "download_url": f"/api/v1/exports/{export_id}/download?token={download_token}",
        "expires_in": 3600,
        "format": req.format
    }
```

---

## 📊 MATRIZ RESUMIDA

```
┌─────────────────────────────────────────────────────────────┐
│ ENDPOINT                    │ AUTH │ ROLES                   │
├─────────────────────────────────────────────────────────────┤
│ POST   /contratos           │ ✅   │ analista, revisor, admin│
│ GET    /contratos           │ ✅   │ visualizador+           │
│ GET    /contratos/{id}      │ ✅   │ visualizador+           │
│ DELETE /contratos/{id}      │ ✅   │ admin                   │
│                             │      │                         │
│ GET    /locations           │ ✅   │ visualizador+           │
│ POST   /locations/distance  │ ✅   │ visualizador+           │
│ POST   /locations           │ ✅   │ analista, revisor, admin│
│                             │      │                         │
│ POST   /parecer             │ ✅   │ analista, revisor, admin│
│ GET    /parecer/{id}        │ ✅   │ visualizador+           │
│ GET    /parecer/{id}/pdf    │ ✅   │ visualizador+           │
│ DELETE /parecer/{id}        │ ✅   │ admin                   │
│                             │      │                         │
│ GET    /bureau/{id}         │ ✅   │ analista+               │
│ POST   /bureau/{id}/export  │ ✅   │ revisor, admin          │
│                             │      │                         │
│ GET    /admin/users         │ ✅   │ admin                   │
│ POST   /admin/users         │ ✅   │ admin                   │
│ DELETE /admin/users/{id}    │ ✅   │ admin                   │
│                             │      │                         │
│ GET    /audit-logs          │ ✅   │ admin                   │
│ GET    /health              │ ❌   │ público (sem auth)      │
│ GET    /metrics             │ ✅   │ admin                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚨 REGRAS OURO

```
1️⃣  SEMPRE validar tenant_id em queries de banco
    ✅ Evita data leakage entre tenants

2️⃣  SEMPRE verificar roles ANTES de operação
    ✅ Garante autorização antes de ação

3️⃣  SEMPRE logar operações sensíveis
    ✅ Compliance + forensics

4️⃣  SEMPRE usar HTTPS em produção
    ✅ Nginx enforce redirect

5️⃣  SEMPRE mascarar PII em responses
    ✅ CPF, email, telefone - nunca completo

6️⃣  NUNCA confiar em input do cliente
    ✅ Validar tipos, ranges, formatos

7️⃣  NUNCA expor detalhes de erro (em prod)
    ✅ "Erro interno" genérico

8️⃣  NUNCA usar rotação manual de tokens
    ✅ Silent renew automático

9️⃣  NUNCA guardar refresh token em cookie
    ✅ Apenas localStorage (SameSite headers)

🔟 NUNCA fazer operação sensível sem auditoria
    ✅ DELETE, EXPORT sempre logado
```

---

## ✅ CHECKLIST PRÉ-PRODUÇÃO

- [ ] Validar token em TODA requisição
- [ ] Validar tenant_id em TODA query
- [ ] Rate limit em TODO endpoint
- [ ] Audit log em TODAS operações sensíveis
- [ ] Roles verificadas antes de operação
- [ ] PII mascarado em responses
- [ ] HTTPS enforçado (Nginx)
- [ ] CORS restritivo (whitelist origins)
- [ ] Soft delete (não hard delete)
- [ ] JWT exp time curto (5min access)
- [ ] Refresh rotation ativado
- [ ] JWKS cache com TTL
- [ ] Testes de segurança passando
- [ ] Audit logs centralizados
- [ ] Monitoring de falhas de auth
- [ ] Documentação de compliance

---

**Status:** 🟢 Pronto para implementação  
**Revisão:** Próxima: 2024-03-03

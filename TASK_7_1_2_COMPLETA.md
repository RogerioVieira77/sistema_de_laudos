"""
TASK 7.1.2 - Models & Database
Data: 2024-02-03
Status: CONCLUÍDA
"""

# 📦 Task 7.1.2 - Models & Database

## ✅ Arquivos Criados/Atualizados

### Novos Modelos

#### 1. **tenant.py** (100 linhas)
Modelo de tenant para suportar multi-tenancy:

```python
class Tenant(Base):
    """Modelo de Tenant para isolação de dados multi-tenant"""
    
    id: String(36)           # UUID único
    name: String(255)        # Nome da organização
    description: String(500) # Descrição opcional
    active: Boolean          # Status ativo/inativo (soft delete)
    created_at: DateTime     # Data de criação
    updated_at: DateTime     # Data de atualização
    
    # Métodos
    to_dict()               # Converter para dict
    create_default()        # Factory de tenant padrão
```

**Recursos:**
- UUID automático
- Soft delete via flag `active`
- Timestamps automáticos
- Índices para performance
- Método `create_default()` para backward compatibility

#### 2. **audit_log.py** (250 linhas)
Modelo de auditoria para compliance e segurança:

```python
class AuditLog(Base):
    """Registro de auditoria de todas as ações"""
    
    id: String(36)              # UUID único
    user_id: String(36)         # ID do usuário (sub JWT)
    user_email: String(255)     # Email (desnormalizado)
    tenant_id: String(36)       # ID do tenant (isolação)
    action: Enum(AuditAction)   # CREATE, READ, UPDATE, DELETE, EXPORT, etc
    resource_type: String(100)  # contrato, parecer, bureau, etc
    resource_id: String(36)     # ID do recurso afetado
    status: Enum(AuditStatus)   # success, error, blocked
    error_message: String(500)  # Mensagem de erro se falhou
    ip_address: String(45)      # IP do cliente
    user_agent: String(500)     # User-Agent do navegador
    details: JSON               # Dados adicionais
    timestamp: DateTime         # Data/hora da ação
    created_at: DateTime        # Data de criação do log
    
    # Enums
    class AuditAction: CREATE, READ, UPDATE, DELETE, EXPORT, DOWNLOAD, UPLOAD, LOGIN
    class AuditStatus: SUCCESS, ERROR, BLOCKED
    
    # Métodos
    to_dict()                   # Converter para dict
    log_action(...)             # Factory method
```

**Recursos:**
- Rastreamento completo de ações
- Enums estruturados para ações e status
- Índices compostos para queries eficientes
- JSON para dados flexíveis
- IP e User-Agent para segurança
- Factory method `log_action()` para facilitar criação

**Índices:**
- tenant_id + action + timestamp (audit reports)
- user_id + timestamp (user activity tracking)
- resource_type + resource_id (resource history)
- timestamp (cleanup automático)

#### 3. **usuario.py** (ATUALIZADO)
Adicionada coluna `tenant_id`:

```python
class Usuario(Base):
    """Usuário do sistema com suporte a multi-tenancy"""
    
    # ... campos existentes ...
    tenant_id: String(36) = "default"  # NOVO - isolação de tenant
    
    # ... índices atualizados ...
    # Adicionados:
    - Index("idx_usuario_tenant_id", "tenant_id")
    - Index("idx_usuario_tenant_email", "tenant_id", "email")
    
    # Novo método
    to_dict()  # Converter para dicionário
```

**Changes:**
- Adicionada coluna `tenant_id` com default "default"
- Adicionados índices para filtrar por tenant
- Adicionado índice composto tenant_id + email
- Adicionado método `to_dict()`
- Atualizado `__repr__` para mostrar tenant_id

### 4. **models/__init__.py** (ATUALIZADO)
Adicionadas novas importações:

```python
from .tenant import Tenant
from .audit_log import AuditLog, AuditAction, AuditStatus

__all__ = [
    # ... existentes ...
    "Tenant",
    "AuditLog",
    "AuditAction",
    "AuditStatus",
]
```

### 5. **migration 002_add_audit_logs.py**
(Criada na Task 7.1.1, pronta para executar)

---

## 📊 Estatísticas

| Item | Valor |
|------|-------|
| Linhas tenant.py | 100 |
| Linhas audit_log.py | 250 |
| Linhas testes | 300+ |
| Classes criadas | 4 (Tenant, AuditLog, AuditAction, AuditStatus) |
| Enums | 2 (AuditAction, AuditStatus) |
| Índices criados | 8+ |
| Métodos utilitários | 6 (to_dict, log_action, create_default, __repr__) |

---

## 🔑 Recursos Principais

### 1. Multi-Tenancy
- ✅ Coluna `tenant_id` em usuarios (default: "default")
- ✅ Coluna `tenant_id` em audit_logs (isolação automática)
- ✅ Índices para queries eficientes por tenant

### 2. Auditoria
- ✅ Todas as ações registradas (CREATE, READ, UPDATE, DELETE, EXPORT, DOWNLOAD)
- ✅ Status rastreado (success, error, blocked)
- ✅ IP e User-Agent armazenados
- ✅ Dados flexíveis em JSON
- ✅ Timestamps precisos para compliance

### 3. Performance
- ✅ Índices compostos para queries comuns
- ✅ Índices por tenant_id para isolação rápida
- ✅ Índices por timestamp para cleanup
- ✅ Índices por resource para history

### 4. Compliance
- ✅ Email desnormalizado (rastrear usuários deletados)
- ✅ Soft delete (coluna `active` em Tenant)
- ✅ Logs imutáveis (insert-only, nunca altera/deleta)
- ✅ LGPD ready (tracks who/what/when)

---

## ✅ Checklist Concluído

Código:
- [x] Tenant model criado (100 linhas)
- [x] AuditLog model criado (250 linhas)
- [x] AuditAction enum com 8 ações
- [x] AuditStatus enum com 3 status
- [x] Usuario.tenant_id adicionado
- [x] Índices para performance
- [x] Métodos to_dict() em todos modelos
- [x] Factory method log_action()
- [x] __repr__ atualizado

Database:
- [x] Migration 002 pronta (criada em 7.1.1)
- [x] Tabela tenants com índices
- [x] Tabela audit_logs com índices compostos
- [x] Coluna tenant_id em usuarios
- [x] Índices para isolação multi-tenant

Testes:
- [x] TestTenant (5 testes)
- [x] TestAuditLog (8 testes)
- [x] TestAuditAction enum
- [x] TestAuditStatus enum
- [x] TestUsuarioExtension (3 testes)
- [x] TestMultiTenancy (3 testes)
- [x] 20+ testes unitários total

Validação:
- [x] tenant.py sintaxe OK
- [x] audit_log.py sintaxe OK
- [x] usuario.py sintaxe OK

---

## 🎯 Pronto Para

**Next Task:** Task 7.2 - FastAPI Dependencies & Decorators

Criar:
- `dependencies.py` com `get_identity()`
- `decorators.py` com `@require_roles()` e `@require_tenant()`
- `error_handlers.py` para 401/403

---

## 📝 Notas Importantes

### 1. Soft Delete Pattern
```python
# Não deletar tenants, apenas marcar como inativo
tenant.active = False
db.commit()

# Queries sempre filtram por active=True
```

### 2. Audit Log Imutável
```python
# Criar novo log
log = AuditLog.log_action(...)
db.add(log)
db.commit()

# NUNCA atualizar ou deletar - apenas inserir!
```

### 3. Multi-Tenancy Obrigatório
```python
# Toda query SEMPRE filtra por tenant
usuarios = db.query(Usuario)\
    .filter(Usuario.tenant_id == identity.tenant_id)\
    ...

# NUNCA esquecer de filtrar!
```

### 4. JSON Details
```python
# Armazenar dados flexíveis
log = AuditLog.log_action(
    ...,
    details={
        "filters": {"status": "pendente"},
        "page": 1,
        "version": 2,
    }
)
```

---

## 🚀 Próximo: Task 7.2

**Tempo Estimado:** 4 horas
**Arquivos:**
- `backend/app/api/dependencies.py` (novo)
- `backend/app/api/decorators.py` (novo)
- `backend/app/api/error_handlers.py` (novo)

**Deliverables:**
- get_identity() dependency
- @require_roles(*roles) decorator
- @require_tenant() decorator
- Error handlers 401/403
- Rate limiter global

---

**Status:** ✅ **TASK 7.1.2 COMPLETA**

Data: 2024-02-03
Tempo: ~3 horas
Próximo: Task 7.2 - FastAPI Dependencies & Decorators

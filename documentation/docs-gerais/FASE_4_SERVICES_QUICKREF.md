# FASE 4.3 - SERVICES LAYER - QUICK REFERENCE

## ✅ CONCLUÍDO COM SUCESSO

**Data:** 2024-01-XX  
**Status:** 100% Completo
**Total de Serviços:** 5 (BaseService + 4 especializados)
**Total de Métodos:** 37

---

## 1. ESTRUTURA DE IMPORTS

```python
# Para usar os serviços no seu código:
from app.services import (
    ContratoService,
    BureauService,
    GeolocalizacaoService,
    PareceService
)

# Exemplo de inicialização
def get_contrato_service(db: Session) -> ContratoService:
    return ContratoService(db)
```

---

## 2. CONTRATO SERVICE - 9 MÉTODOS

```python
service = ContratoService(db)

# CRUD
service.create_contrato(contrato_data, usuario_id)           # POST
service.get_contrato(contrato_id)                            # GET /id
service.search_contratos(search_term, skip, limit)           # GET /search
service.delete_contrato(contrato_id)                         # DELETE

# Usuário
service.get_contratos_usuario(usuario_id, skip, limit)       # GET /usuario

# Status & Localização
service.get_contratos_por_status(status, skip, limit)        # GET /status
service.atualizar_status(contrato_id, novo_status, usuario_id)
service.atualizar_localizacao(contrato_id, lat, lon, usuario_id)

# Histórico
service.get_contratos_recentes(dias=7)                       # GET /recent
```

---

## 3. BUREAU SERVICE - 9 MÉTODOS

```python
service = BureauService(db)

# CRUD
service.criar_bureau_data(bureau_data, usuario_id)           # POST
service.obter_bureau_data(bureau_id)                         # GET /id
service.obter_por_contrato(contrato_id)                      # GET /contrato
service.deletar_bureau_data(bureau_id)                       # DELETE

# Busca
service.buscar_por_cpf(cpf)                                  # GET /cpf
service.buscar_por_nome(nome, skip, limit)                   # GET /search

# Geocodificação
service.geocodificar_endereco_bureau(bureau_id, usuario_id)  # POST /geocode
service.obter_sem_localizacao(skip, limit)                   # GET /ungeocoded

# Estatísticas
service.get_estatisticas_bureau()                            # GET /stats
```

---

## 4. GEOLOCALIZAÇÃO SERVICE - 6 MÉTODOS

```python
service = GeolocalizacaoService(db)

# Análise (Main Method)
service.analisar_geolocalizacao(contrato_id, usuario_id)     # POST /analyze

# Cálculos
service.calcular_distancia(lat1, lon1, lat2, lon2)           # Haversine
service.obter_parecer_type(distancia_km)                     # Type por distância

# Geocodificação
service.geocodificar_endereco(endereco)                      # Address → Lat/Lon
service.reverse_geocodificar(latitude, longitude)            # Lat/Lon → Address

# Estatísticas
service.get_estatisticas_geolocalizacao()                    # GET /stats
```

---

## 5. PARECER SERVICE - 10 MÉTODOS

```python
service = PareceService(db)

# CRUD
service.criar_parecer(parecer_data, usuario_id)              # POST
service.obter_parecer(parecer_id)                            # GET /id
service.atualizar_parecer(parecer_id, update_data, usuario_id)
service.deletar_parecer(parecer_id)                          # DELETE

# Busca por Contrato
service.obter_pareceres_contrato(contrato_id)                # GET /contrato

# Filtros
service.obter_por_tipo(tipo, skip, limit)                    # GET /tipo
service.obter_por_faixa_distancia(min_km, max_km, skip, limit)
service.filtrar_pareceres(filtro, skip, limit)               # Advanced filter

# Estatísticas
service.get_estatisticas_pareceres()                         # GET /stats
service.contar_por_tipo(tipo)                                # GET /count/{tipo}
```

---

## 6. TIPOS DE PARECER

```
PROXIMAL       = ≤ 5 km
MODERADO       = 5-20 km
DISTANTE       = 20-50 km
MUITO_DISTANTE = > 50 km
```

---

## 7. EXEMPLO DE USO COMPLETO

```python
from sqlalchemy.orm import Session
from app.services import (
    ContratoService,
    BureauService,
    GeolocalizacaoService,
    PareceService
)
from app.schemas import DadosContratoCreate, DadosBureauCreate

def process_contrato_workflow(db: Session, usuario_id: int):
    """Exemplo de workflow completo"""
    
    # 1. Criar contrato
    contrato_service = ContratoService(db)
    contrato_data = DadosContratoCreate(
        numero_contrato="CONT123",
        cpf_cliente="12345678900",
        latitude=Decimal("-23.5505"),
        longitude=Decimal("-46.6333"),
        endereco_assinatura="Rua A, 123, SP",
        status="PENDENTE"
    )
    contrato = contrato_service.create_contrato(contrato_data, usuario_id)
    
    # 2. Adicionar dados de bureau
    bureau_service = BureauService(db)
    bureau_data = DadosBureauCreate(
        contrato_id=contrato.id,
        cpf_cliente="12345678900",
        nome_cliente="João Silva",
        logradouro="Rua B, 456, SP"
    )
    bureau = bureau_service.criar_bureau_data(bureau_data, usuario_id)
    
    # 3. Geocodificar bureau
    bureau_geocoded = bureau_service.geocodificar_endereco_bureau(bureau.id, usuario_id)
    
    # 4. Analisar geolocalização
    geo_service = GeolocalizacaoService(db)
    analysis = geo_service.analisar_geolocalizacao(contrato.id, usuario_id)
    
    # 5. Obter parecer criado
    parecer_service = PareceService(db)
    parecer = parecer_service.obter_pareceres_contrato(contrato.id)
    
    return {
        "contrato": contrato,
        "bureau": bureau_geocoded,
        "analise": analysis,
        "parecer": parecer
    }
```

---

## 8. TRATAMENTO DE ERROS

Todos os serviços fazem logging e re-lançam exceções:

```python
try:
    resultado = service.operacao(dados)
except ValueError as e:
    # Recurso não encontrado
    # → Lançar 404 na camada de API
    pass
except Exception as e:
    # Erro inesperado
    # → Lançar 500 na camada de API
    pass
```

---

## 9. PAGINAÇÃO

Métodos de busca retornam `ListResponse` com paginação:

```python
response = service.obter_por_tipo("PROXIMAL", skip=0, limit=10)
# response.total = 42
# response.pareceres = [...]
```

---

## 10. LOGGING

Todos os eventos são registrados:

```python
# Visível em logs estruturados
"Created contract XYZ"
"Error creating bureau data: database error"
"Analyzed geolocation for contract ABC"
```

---

## 11. PRÓXIMAS FASES

### Phase 4.4: API Endpoints
Será criado:
```
backend/app/api/v1/
├── contratos.py       # Router para contratos
├── bureau.py          # Router para bureau
├── geolocalização.py  # Router para análise
└── pareceres.py       # Router para pareceres
```

### Phase 5: Frontend
React + Vite com consumo das APIs

---

## 12. VERIFICAÇÃO

```bash
# Verificar importações
docker compose exec -T backend python -c "from app.services import *; print('OK')"

# Listar métodos
docker compose exec -T backend python -c "
from app.services import ContratoService
service = ContratoService
methods = [m for m in dir(service) if not m.startswith('_')]
for m in methods: print(m)
"
```

---

**Status:** ✅ Todos os 37 métodos implementados e testados
**Documentação:** [FASE_4_SERVICES.md](FASE_4_SERVICES.md)
**Checkpoint:** [FASE_4_SERVICES_CHECKPOINT.md](FASE_4_SERVICES_CHECKPOINT.md)

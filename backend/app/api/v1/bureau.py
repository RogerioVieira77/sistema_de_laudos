"""
Bureau Router - API endpoints for bureau data management

Autenticação: Todos os endpoints requerem JWT Bearer token (get_identity)
Autorização: Usuarios com roles: analista, revisor, admin
Isolação: Todos dados filtrados por tenant_id do usuario autenticado
Rate Limiting: Read limitado a 50 req/min
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.dependencies import get_db, get_identity
from app.api.decorators import require_roles, require_tenant
from app.api.rate_limiting import limiter, RateLimits
from app.core.oidc_models import Identity
from app.core.exceptions import (
    BureauNaoEncontrado,
    ContratoNaoEncontrado,
    SemPermissao,
)
from app.services import BureauService, ContratoService
from app.schemas import DadosBureauResponse

router = APIRouter(
    prefix="/bureau",
    tags=["Bureau"],
    responses={404: {"description": "Bureau não encontrado"}},
)


def get_bureau_service(db: Session = Depends(get_db)) -> BureauService:
    """Dependency for BureauService injection"""
    return BureauService(db)


def get_contrato_service(db: Session = Depends(get_db)) -> ContratoService:
    """Dependency for ContratoService injection"""
    return ContratoService(db)


@router.get(
    "/{contrato_id}",
    response_model=DadosBureauResponse,
    summary="Obter Dados de Bureau",
    description="Busca dados de bureau para um contrato específico",
    responses={
        200: {"description": "Dados de bureau encontrados"},
        404: {"description": "Bureau não encontrado ou contrato inválido"},
        403: {"description": "Sem permissão"},
        429: {"description": "Muitas requisições. Limite: 50 por minuto"},
    }
)
@require_tenant()
@limiter.limit(RateLimits.READ)
async def get_bureau(
    request,  # Necessário para rate limiting
    contrato_id: int,
    identity: Identity = Depends(get_identity),
    bureau_service: BureauService = Depends(get_bureau_service),
    contrato_service: ContratoService = Depends(get_contrato_service),
):
    """
    Obtém dados de bureau para um contrato específico.
    
    Requer autenticação (JWT Bearer token).
    
    ### Parâmetros:
    - **contrato_id**: ID do contrato
    
    ### Response:
    - Dados do cliente consultado em bureau:
      - id: ID do registro
      - contrato_id: ID do contrato relacionado
      - cpf_cliente: CPF do cliente
      - nome_cliente: Nome do cliente
      - logradouro: Endereço do cliente
      - cep: CEP do endereço
      - telefone: Telefone do cliente
      - latitude/longitude: Coordenadas geocodificadas
      - data_consulta: Quando foi consultado
    
    ### Erros:
    - 404: Bureau não encontrado ou contrato inválido
    - 403: Você não tem permissão para acessar este contrato
    """
    
    # Verificar se contrato pertence ao tenant do usuário
    contrato = contrato_service.get_contrato(contrato_id)
    if not contrato:
        raise ContratoNaoEncontrado(contrato_id)
    
    if contrato.tenant_id != identity.tenant_id:
        raise SemPermissao("Você não tem permissão para acessar este contrato")
    
    # Buscar dados de bureau
    bureau = bureau_service.get_by_contrato(contrato_id)
    if not bureau:
        raise BureauNaoEncontrado(contrato_id)
    
    return bureau


@router.get(
    "",
    summary="Listar Dados de Bureau",
    description="Lista todos os registros de bureau do usuário com paginação",
    responses={
        200: {"description": "Lista de dados de bureau"},
        429: {"description": "Muitas requisições. Limite: 50 por minuto"},
    }
)
@require_tenant()
@limiter.limit(RateLimits.READ)
async def list_bureau(
    request,  # Necessário para rate limiting
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(10, ge=1, le=100, description="Número de registros a retornar"),
    cpf: Optional[str] = Query(None, description="Filtrar por CPF"),
    identity: Identity = Depends(get_identity),
    bureau_service: BureauService = Depends(get_bureau_service),
    contrato_service: ContratoService = Depends(get_contrato_service),
):
    """
    Lista todos os registros de bureau associados aos contratos do usuário.
    
    Requer autenticação (JWT Bearer token).
    Retorna apenas registros de bureau do tenant do usuário (tenant_id automaticamente filtrado).
    
    ### Parâmetros:
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Número de registros a retornar (padrão: 10, máx: 100)
    - **cpf**: Filtrar por CPF (opcional)
    
    ### Response:
    - **total**: Total de registros
    - **skip**: Página atual
    - **limit**: Registros por página
    - **items**: Lista de dados de bureau (filtrados por tenant_id)
    """
    
    # Buscar todos os contratos do tenant
    contratos = contrato_service.get_contratos_tenant(identity.tenant_id, skip=0, limit=1000)
    contrato_ids = [c.id for c in contratos.contratos]
    
    if not contrato_ids:
        return {
            "total": 0,
            "skip": skip,
            "limit": limit,
            "items": []
        }
    
    # Buscar dados de bureau para os contratos
    items, total = bureau_service.list_by_contratos(
        contrato_ids,
        skip=skip,
        limit=limit,
        tenant_id=identity.tenant_id
    )
    
    # Filtrar por CPF se especificado
    if cpf:
        cpf_limpo = cpf.replace(".", "").replace("-", "").replace("/", "")
        items = [b for b in items if cpf_limpo in b.cpf_cliente]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items
    }

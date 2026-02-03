"""
Bureau Router - API endpoints for bureau data management
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.dependencies import get_db, get_current_user
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
    }
)
async def get_bureau(
    contrato_id: int,
    current_user_id: int = Depends(get_current_user),
    bureau_service: BureauService = Depends(get_bureau_service),
    contrato_service: ContratoService = Depends(get_contrato_service),
):
    """
    Obtém dados de bureau para um contrato específico.
    
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
    
    # Verificar se contrato pertence ao usuário
    contrato = contrato_service.get_contrato(contrato_id)
    if not contrato:
        raise ContratoNaoEncontrado(contrato_id)
    
    if contrato.usuario_id != current_user_id:
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
    }
)
async def list_bureau(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(10, ge=1, le=100, description="Número de registros a retornar"),
    cpf: Optional[str] = Query(None, description="Filtrar por CPF"),
    current_user_id: int = Depends(get_current_user),
    bureau_service: BureauService = Depends(get_bureau_service),
    contrato_service: ContratoService = Depends(get_contrato_service),
):
    """
    Lista todos os registros de bureau associados aos contratos do usuário.
    
    ### Parâmetros:
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Número de registros a retornar (padrão: 10, máx: 100)
    - **cpf**: Filtrar por CPF (opcional)
    
    ### Response:
    - **total**: Total de registros
    - **skip**: Página atual
    - **limit**: Registros por página
    - **items**: Lista de dados de bureau
    """
    
    # Buscar todos os contratos do usuário
    contratos = contrato_service.get_contratos_usuario(current_user_id, skip=0, limit=1000)
    contrato_ids = [c.id for c in contratos.contratos]
    
    if not contrato_ids:
        return {
            "total": 0,
            "skip": skip,
            "limit": limit,
            "items": []
        }
    
    # Buscar dados de bureau para os contratos
    items, total = bureau_service.list_by_contratos(contrato_ids, skip=skip, limit=limit)
    
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

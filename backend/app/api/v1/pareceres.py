"""
Pareceres Router - API endpoints for parecer (opinion) management
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.api.dependencies import get_db, get_current_user
from app.core.exceptions import (
    PareceNaoEncontrado,
    ContratoNaoEncontrado,
    SemPermissao,
)
from app.services import PareceService, ContratoService
from app.schemas import PareceResponse

router = APIRouter(
    prefix="/pareceres",
    tags=["Pareceres"],
    responses={404: {"description": "Parecer não encontrado"}},
)


def get_parecer_service(db: Session = Depends(get_db)) -> PareceService:
    """Dependency for PareceService injection"""
    return PareceService(db)


def get_contrato_service(db: Session = Depends(get_db)) -> ContratoService:
    """Dependency for ContratoService injection"""
    return ContratoService(db)


@router.get(
    "",
    summary="Listar Pareceres",
    description="Lista todos os pareceres do usuário com filtros e paginação",
    responses={
        200: {"description": "Lista de pareceres"},
    }
)
async def list_pareceres(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(10, ge=1, le=100, description="Número de registros a retornar"),
    tipo_parecer: Optional[str] = Query(
        None,
        description="Filtrar por tipo (PROXIMAL, MODERADO, DISTANTE, MUITO_DISTANTE)"
    ),
    data_inicio: Optional[datetime] = Query(None, description="Filtrar por data inicial"),
    data_fim: Optional[datetime] = Query(None, description="Filtrar por data final"),
    ordenar_por: str = Query(
        "data",
        regex="^(data|distancia|tipo)$",
        description="Campo para ordenação"
    ),
    current_user_id: int = Depends(get_current_user),
    service: PareceService = Depends(get_parecer_service),
    contrato_service: ContratoService = Depends(get_contrato_service),
):
    """
    Lista todos os pareceres do usuário com suporte a filtros e paginação.
    
    ### Parâmetros:
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Número de registros a retornar (padrão: 10, máx: 100)
    - **tipo_parecer**: Filtrar por tipo (PROXIMAL|MODERADO|DISTANTE|MUITO_DISTANTE)
    - **data_inicio**: Filtrar pareceres após esta data (ISO 8601)
    - **data_fim**: Filtrar pareceres antes desta data (ISO 8601)
    - **ordenar_por**: Ordenar por (data|distancia|tipo)
    
    ### Response:
    - **total**: Total de pareceres
    - **skip**: Página atual
    - **limit**: Registros por página
    - **items**: Lista de pareceres
    
    ### Exemplo de Filtro:
    ```
    GET /api/v1/pareceres?tipo_parecer=PROXIMAL&limite=5&ordenar_por=data
    ```
    """
    
    # Buscar contratos do usuário
    contratos = contrato_service.get_contratos_usuario(current_user_id, skip=0, limit=1000)
    contrato_ids = [c.id for c in contratos.contratos]
    
    if not contrato_ids:
        return {
            "total": 0,
            "skip": skip,
            "limit": limit,
            "items": []
        }
    
    # Buscar pareceres
    items, total = service.list_by_contratos(
        contrato_ids,
        skip=skip,
        limit=limit,
        tipo_parecer=tipo_parecer,
        data_inicio=data_inicio,
        data_fim=data_fim,
        ordenar_por=ordenar_por
    )
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items
    }


@router.get(
    "/{parecer_id}",
    response_model=PareceResponse,
    summary="Obter Parecer",
    description="Obtém um parecer específico pelo ID",
    responses={
        200: {"description": "Parecer encontrado"},
        404: {"description": "Parecer não encontrado"},
        403: {"description": "Sem permissão"},
    }
)
async def get_parecer(
    parecer_id: int,
    current_user_id: int = Depends(get_current_user),
    service: PareceService = Depends(get_parecer_service),
    contrato_service: ContratoService = Depends(get_contrato_service),
):
    """
    Obtém detalhes completos de um parecer específico.
    
    ### Parâmetros:
    - **parecer_id**: ID do parecer a buscar
    
    ### Response:
    - **id**: ID do parecer
    - **contrato_id**: ID do contrato associado
    - **distancia_km**: Distância em quilômetros
    - **tipo_parecer**: Tipo do parecer
    - **texto_parecer**: Descrição do parecer
    - **latitude_inicio/longitude_inicio**: Coordenadas do contrato
    - **latitude_fim/longitude_fim**: Coordenadas do bureau
    - **criado_em**: Data de criação
    
    ### Erros:
    - 404: Parecer não encontrado
    - 403: Sem permissão
    """
    
    parecer = service.obter_parecer(parecer_id)
    if not parecer:
        raise PareceNaoEncontrado(parecer_id)
    
    # Verificar se o contrato pertence ao usuário
    contrato = contrato_service.get_contrato(parecer.contrato_id)
    if not contrato or contrato.usuario_id != current_user_id:
        raise SemPermissao("Você não tem permissão para acessar este parecer")
    
    return parecer


@router.get(
    "/estatisticas/resumo",
    summary="Estatísticas de Pareceres",
    description="Obtém estatísticas agregadas dos pareceres do usuário",
    responses={
        200: {"description": "Estatísticas calculadas"},
    }
)
async def get_estatisticas(
    current_user_id: int = Depends(get_current_user),
    service: PareceService = Depends(get_parecer_service),
    contrato_service: ContratoService = Depends(get_contrato_service),
):
    """
    Retorna estatísticas agregadas dos pareceres.
    
    ### Response:
    - **total_pareceres**: Total de pareceres gerados
    - **por_tipo**: Contagem por tipo de parecer
      - PROXIMAL: número
      - MODERADO: número
      - DISTANTE: número
      - MUITO_DISTANTE: número
    - **distancia_media_km**: Distância média
    - **distancia_minima_km**: Distância mínima
    - **distancia_maxima_km**: Distância máxima
    
    ### Exemplo de Response:
    ```json
    {
      "total_pareceres": 50,
      "por_tipo": {
        "PROXIMAL": 20,
        "MODERADO": 15,
        "DISTANTE": 10,
        "MUITO_DISTANTE": 5
      },
      "distancia_media_km": 45.3,
      "distancia_minima_km": 0.5,
      "distancia_maxima_km": 250.8
    }
    ```
    """
    
    # Buscar contratos do usuário
    contratos = contrato_service.get_contratos_usuario(current_user_id, skip=0, limit=1000)
    contrato_ids = [c.id for c in contratos.contratos]
    
    if not contrato_ids:
        return {
            "total_pareceres": 0,
            "por_tipo": {
                "PROXIMAL": 0,
                "MODERADO": 0,
                "DISTANTE": 0,
                "MUITO_DISTANTE": 0
            },
            "distancia_media_km": 0,
            "distancia_minima_km": 0,
            "distancia_maxima_km": 0
        }
    
    # Buscar estatísticas
    stats = service.get_estatisticas(contrato_ids)
    return stats


@router.delete(
    "/{parecer_id}",
    status_code=204,
    summary="Deletar Parecer",
    description="Deleta um parecer específico",
    responses={
        204: {"description": "Parecer deletado com sucesso"},
        404: {"description": "Parecer não encontrado"},
        403: {"description": "Sem permissão"},
    }
)
async def delete_parecer(
    parecer_id: int,
    current_user_id: int = Depends(get_current_user),
    service: PareceService = Depends(get_parecer_service),
    contrato_service: ContratoService = Depends(get_contrato_service),
):
    """
    Deleta um parecer específico.
    
    ### Parâmetros:
    - **parecer_id**: ID do parecer a deletar
    
    ### Response:
    - 204: Deletado com sucesso (sem corpo)
    
    ### Erros:
    - 404: Parecer não encontrado
    - 403: Sem permissão
    """
    
    parecer = service.obter_parecer(parecer_id)
    if not parecer:
        raise PareceNaoEncontrado(parecer_id)
    
    # Verificar se o contrato pertence ao usuário
    contrato = contrato_service.get_contrato(parecer.contrato_id)
    if not contrato or contrato.usuario_id != current_user_id:
        raise SemPermissao("Você não tem permissão para deletar este parecer")
    
    service.delete_parecer(parecer_id)

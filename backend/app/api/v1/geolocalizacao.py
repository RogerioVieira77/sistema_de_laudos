"""
Geolocalização Router - API endpoints for geolocation analysis

Autenticação: Todos os endpoints requerem JWT Bearer token (get_identity)
Autorização: Usuarios com roles: analista, revisor, admin
Isolação: Todos dados filtrados por tenant_id do usuario autenticado
Rate Limiting: POST (análise) 10 req/min, GET (read) 50 req/min
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

from app.api.dependencies import get_db, get_identity
from app.api.decorators import require_roles, require_tenant
from app.api.rate_limiting import limiter, RateLimits
from app.core.oidc_models import Identity
from app.core.exceptions import (
    ContratoNaoEncontrado,
    BureauNaoEncontrado,
    DadosInsuficientes,
    SemPermissao,
    ServicoGeocodificacaoIndisponivel,
)
from app.services import (
    GeolocalizacaoService,
    ContratoService,
    BureauService,
)

router = APIRouter(
    prefix="/geolocalizacao",
    tags=["Geolocalização"],
    responses={404: {"description": "Recurso não encontrado"}},
)


class GeolocationAnalysisRequest(BaseModel):
    """Request schema for geolocation analysis"""
    contrato_id: int
    forcar_atualizacao: bool = False


class GeolocationAnalysisResponse(BaseModel):
    """Response schema for geolocation analysis"""
    contrato_id: int
    endereco_origem: str
    endereco_destino: str
    latitude_origem: Decimal
    longitude_origem: Decimal
    latitude_destino: Decimal
    longitude_destino: Decimal
    distancia_km: Decimal
    tipo_parecer: str
    texto_parecer: str
    confianca: Optional[Decimal] = None
    rota: list = []
    timestamp: str


def get_geolocalizacao_service(db: Session = Depends(get_db)) -> GeolocalizacaoService:
    """Dependency for GeolocalizacaoService injection"""
    return GeolocalizacaoService(db)


def get_contrato_service(db: Session = Depends(get_db)) -> ContratoService:
    """Dependency for ContratoService injection"""
    return ContratoService(db)


def get_bureau_service(db: Session = Depends(get_db)) -> BureauService:
    """Dependency for BureauService injection"""
    return BureauService(db)


@router.post(
    "/analisar",
    response_model=GeolocationAnalysisResponse,
    summary="Analisar Geolocalização",
    description="Realiza análise de geolocalização entre contrato e bureau",
    responses={
        200: {"description": "Análise realizada com sucesso"},
        404: {"description": "Contrato ou Bureau não encontrado"},
        422: {"description": "Dados insuficientes para análise"},
        429: {"description": "Muitas análises. Limite: 10 por minuto"},
        503: {"description": "Serviço de geocodificação indisponível"},
    }
)
@require_roles("analista", "revisor", "admin")
@require_tenant()
@limiter.limit(RateLimits.UPLOAD)
async def analisar_geolocalizacao(
    request: GeolocationAnalysisRequest,
    req,  # Necessário para rate limiting
    identity: Identity = Depends(get_identity),
    geo_service: GeolocalizacaoService = Depends(get_geolocalizacao_service),
    contrato_service: ContratoService = Depends(get_contrato_service),
    bureau_service: BureauService = Depends(get_bureau_service),
):
    """
    Realiza análise de geolocalização comparando endereço do contrato com bureau.
    Rate limit: 10 análises por minuto
    
    Requer autenticação (JWT Bearer token) e roles: analista, revisor ou admin.
    
    ### Fluxo:
    1. Busca dados_contrato
    2. Busca dados_bureau
    3. Calcula distância (Haversine)
    4. Gera parecer baseado em regras de negócio
    5. Salva resultado em pareceres
    6. Retorna análise completa
    
    ### Request:
    - **contrato_id**: ID do contrato a analisar
    - **forcar_atualizacao**: Se True, recalcula mesmo se já analisado
    
    ### Response:
    - **contrato_id**: ID do contrato
    - **endereco_origem**: Endereço do contrato
    - **endereco_destino**: Endereço do bureau
    - **distancia_km**: Distância em quilômetros
    - **tipo_parecer**: PROXIMAL, MODERADO, DISTANTE, MUITO_DISTANTE
    - **texto_parecer**: Descrição do parecer
    - **confianca**: Nível de confiança da análise (0-1)
    - **timestamp**: Data/hora da análise
    
    ### Erros:
    - 404: Contrato ou Bureau não encontrado
    - 422: Dados insuficientes (faltam coordenadas)
    - 503: Serviço de geocodificação indisponível
    - 403: Sem permissão
    """
    
    try:
        # Verificar se contrato pertence ao tenant do usuário
        contrato = contrato_service.get_contrato(request.contrato_id)
        if not contrato:
            raise ContratoNaoEncontrado(request.contrato_id)
        
        if contrato.tenant_id != identity.tenant_id:
            raise SemPermissao("Você não tem permissão para analisar este contrato")
        
        # Verificar se existem dados de bureau
        bureau = bureau_service.get_by_contrato(request.contrato_id)
        if not bureau:
            raise BureauNaoEncontrado(request.contrato_id)
        
        # Validar se temos coordenadas
        if not contrato.latitude or not contrato.longitude:
            raise DadosInsuficientes("Contrato não possui coordenadas")
        
        if not bureau.latitude or not bureau.longitude:
            raise DadosInsuficientes("Bureau não possui coordenadas geocodificadas")
        
        # Realizar análise
        resultado = geo_service.analisar(
            contrato_id=request.contrato_id,
            forcar_atualizacao=request.forcar_atualizacao,
            usuario_id=identity.sub,  # Use UUID from JWT
            tenant_id=identity.tenant_id  # Include tenant_id
        )
        
        return resultado
        
    except (ContratoNaoEncontrado, BureauNaoEncontrado, DadosInsuficientes, SemPermissao):
        raise
    except Exception as e:
        if "serviço" in str(e).lower() or "geocod" in str(e).lower():
            raise ServicoGeocodificacaoIndisponivel()
        raise


@router.get(
    "/{contrato_id}",
    summary="Obter Análise de Geolocalização",
    description="Obtém a análise de geolocalização para um contrato",
    responses={
        200: {"description": "Análise encontrada"},
        404: {"description": "Contrato ou análise não encontrada"},
        403: {"description": "Sem permissão"},
        429: {"description": "Muitas requisições. Limite: 50 por minuto"},
    }
)
@require_tenant()
@limiter.limit(RateLimits.READ)
async def get_geolocalizacao(
    request,  # Necessário para rate limiting
    contrato_id: int,
    identity: Identity = Depends(get_identity),
    geo_service: GeolocalizacaoService = Depends(get_geolocalizacao_service),
    contrato_service: ContratoService = Depends(get_contrato_service),
):
    """
    Obtém a análise de geolocalização já realizada para um contrato.
    
    Requer autenticação (JWT Bearer token).
    Rate limit: 50 requisições por minuto
    
    ### Parâmetros:
    - **contrato_id**: ID do contrato
    
    ### Response:
    - Dados da análise anterior:
      - contrato_id
      - distancia_km
      - tipo_parecer
      - ultima_atualizacao
    
    ### Erros:
    - 404: Contrato ou análise não encontrada
    - 403: Sem permissão
    """
    
    # Verificar se contrato pertence ao tenant
    contrato = contrato_service.get_contrato(contrato_id)
    if not contrato:
        raise ContratoNaoEncontrado(contrato_id)
    
    if contrato.tenant_id != identity.tenant_id:
        raise SemPermissao("Você não tem permissão para acessar este contrato")
    
    # Buscar análise anterior
    resultado = geo_service.obter_analise(contrato_id)
    if not resultado:
        raise ContratoNaoEncontrado(contrato_id)
    
    return resultado

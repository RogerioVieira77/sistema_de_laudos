"""
Contratos Router - API endpoints for contract management

Autenticação: Todos os endpoints requerem JWT Bearer token (get_identity)
Autorização: Usuarios com roles: analista, revisor, admin
Isolação: Todos contratos filtrados por tenant_id do usuario autenticado
Rate Limiting: Upload e delete limitados a 10 req/min, others 50 req/min
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.api.dependencies import get_db, get_identity
from app.api.decorators import require_roles, require_tenant
from app.api.rate_limiting import limiter, RateLimits
from app.core.oidc_models import Identity
from app.core.exceptions import (
    ContratoNaoEncontrado,
    ArquivoInvalido,
    SemPermissao,
    ErroInterno,
)
from app.services import ContratoService
from app.schemas import (
    DadosContratoCreate,
    DadosContratoResponse,
)

router = APIRouter(
    prefix="/contratos",
    tags=["Contratos"],
    responses={404: {"description": "Contrato não encontrado"}},
)


def get_contrato_service(db: Session = Depends(get_db)) -> ContratoService:
    """Dependency for ContratoService injection"""
    return ContratoService(db)


@router.post(
    "/upload",
    response_model=DadosContratoResponse,
    status_code=201,
    summary="Upload de Contrato",
    description="Faz upload de um arquivo PDF de contrato e extrai dados",
    responses={
        201: {"description": "Contrato criado com sucesso"},
        400: {"description": "Arquivo inválido ou muito grande"},
        413: {"description": "Arquivo muito grande (> 10MB)"},
        429: {"description": "Muitos uploads. Limite: 10 por minuto"},
        500: {"description": "Erro ao extrair dados do PDF"},
    }
)
@require_roles("analista", "revisor", "admin")
@require_tenant()
@limiter.limit(RateLimits.UPLOAD)
async def upload_contrato(
    request,  # Necessário para rate limiting
    file: UploadFile = File(
        ...,
        description="Arquivo PDF do contrato",
        media_type="application/pdf"
    ),
    numero_contrato: str = Query(
        ...,
        min_length=1,
        max_length=50,
        description="Número do contrato"
    ),
    cpf_cliente: str = Query(
        ...,
        min_length=11,
        max_length=14,
        description="CPF do cliente (com ou sem formatação)"
    ),
    identity: Identity = Depends(get_identity),
    service: ContratoService = Depends(get_contrato_service),
):
    """
    Faz upload de um contrato em formato PDF.
    
    Requer autenticação (JWT Bearer token) e roles: analista, revisor ou admin.
    Rate limit: 10 uploads por minuto
    
    ### Fluxo:
    1. Valida arquivo (tipo, tamanho)
    2. Salva arquivo no servidor
    3. Extrai dados (CPF, número, coordenadas)
    4. Salva em dados_contrato com tenant_id automaticamente
    5. Retorna ID para referência
    
    ### Parâmetros:
    - **file**: Arquivo PDF (obrigatório, máx 10MB)
    - **numero_contrato**: Número único do contrato
    - **cpf_cliente**: CPF do cliente (11 dígitos)
    
    ### Response:
    - **id**: ID do contrato criado
    - **usuario_id**: ID do usuário proprietário
    - **numero_contrato**: Número do contrato
    - **cpf_cliente**: CPF do cliente
    - **latitude/longitude**: Coordenadas do endereço
    - **criado_em**: Data de criação
    """
    
    try:
        # Validar tipo de arquivo
        if file.content_type not in ["application/pdf"]:
            raise ArquivoInvalido("Apenas arquivos PDF são aceitos")
        
        # Validar tamanho (10MB máximo)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        
        if len(file_content) > MAX_FILE_SIZE:
            raise ArquivoInvalido("Arquivo maior que 10MB")
        
        if len(file_content) == 0:
            raise ArquivoInvalido("Arquivo vazio")
        
        # Normalizar CPF (remover formatação)
        cpf_limpo = cpf_cliente.replace(".", "").replace("-", "").replace("/", "")
        if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
            raise ArquivoInvalido("CPF inválido")
        
        # Salvar arquivo no servidor
        upload_dir = f"/uploads/contratos/{identity.tenant_id}"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{identity.sub}_{numero_contrato}.pdf")
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Criar contrato no banco (tenant_id será preenchido automaticamente pelo modelo)
        contrato_data = DadosContratoCreate(
            usuario_id=identity.sub,  # User UUID from JWT
            numero_contrato=numero_contrato,
            cpf_cliente=cpf_limpo,
            endereco_assinatura="Extraído do PDF",
            arquivo_pdf_path=file_path,
            latitude=None,  # TODO: Extrair do PDF
            longitude=None,  # TODO: Extrair do PDF
            tenant_id=identity.tenant_id,  # Automatic tenant isolation
        )
        
        contrato_response = service.create_contrato(contrato_data)
        return contrato_response
        
    except ArquivoInvalido:
        raise
    except Exception as e:
        raise ErroInterno(f"Erro ao processar contrato: {str(e)}")


@router.get(
    "/{contrato_id}",
    response_model=DadosContratoResponse,
    summary="Obter Contrato",
    description="Busca um contrato específico pelo ID",
    responses={
        200: {"description": "Contrato encontrado"},
        404: {"description": "Contrato não encontrado"},
        403: {"description": "Sem permissão"},
        429: {"description": "Muitas requisições. Limite: 50 por minuto"},
    }
)
@require_tenant()
@limiter.limit(RateLimits.READ)
async def get_contrato(
    request,  # Necessário para rate limiting
    contrato_id: int,
    identity: Identity = Depends(get_identity),
    service: ContratoService = Depends(get_contrato_service),
):
    """
    Obtém um contrato específico.
    
    Requer autenticação (JWT Bearer token).
    Garante isolação de tenant automaticamente.
    Rate limit: 50 requisições por minuto
    
    ### Parâmetros:
    - **contrato_id**: ID do contrato a buscar
    
    ### Response:
    - Dados completos do contrato
    
    ### Erros:
    - 404: Contrato não encontrado
    - 403: Você não tem permissão para acessar este contrato
    """
    
    contrato = service.get_contrato(contrato_id)
    
    if not contrato:
        raise ContratoNaoEncontrado(contrato_id)
    
    # Validar tenant_id (multi-tenancy isolation)
    if contrato.tenant_id != identity.tenant_id:
        raise SemPermissao("Este contrato não pertence ao seu tenant")
    
    return contrato


@router.get(
    "",
    summary="Listar Contratos",
    description="Lista todos os contratos do usuário com paginação",
    responses={
        200: {"description": "Lista de contratos"},
        429: {"description": "Muitas requisições. Limite: 50 por minuto"},
    }
)
@require_tenant()
@limiter.limit(RateLimits.READ)
async def list_contratos(
    request,  # Necessário para rate limiting
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(10, ge=1, le=100, description="Número de registros a retornar"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    identity: Identity = Depends(get_identity),
    service: ContratoService = Depends(get_contrato_service),
):
    """
    Lista todos os contratos do usuário autenticado.
    
    Requer autenticação (JWT Bearer token).
    Retorna apenas contratos do tenant do usuário (tenant_id automaticamente filtrado).
    
    ### Parâmetros:
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Número de registros a retornar (padrão: 10, máx: 100)
    - **status**: Filtrar por status (opcional)
    
    ### Response:
    - **total**: Total de contratos
    - **skip**: Página atual
    - **limit**: Registros por página
    - **contratos**: Lista de contratos (filtrados por tenant_id)
    """
    
    # Query automaticamente filtrada por tenant_id
    resultado = service.get_contratos_tenant(
        identity.tenant_id,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return {
        "total": resultado.total,
        "skip": skip,
        "limit": limit,
        "contratos": resultado.contratos
    }


@router.delete(
    "/{contrato_id}",
    status_code=204,
    summary="Deletar Contrato",
    description="Deleta um contrato específico",
    responses={
        204: {"description": "Contrato deletado com sucesso"},
        404: {"description": "Contrato não encontrado"},
        403: {"description": "Sem permissão"},
        429: {"description": "Muitos deletes. Limite: 10 por minuto"},
    }
)
@require_roles("revisor", "admin")
@require_tenant()
@limiter.limit(RateLimits.DELETE)
async def delete_contrato(
    request,  # Necessário para rate limiting
    contrato_id: int,
    identity: Identity = Depends(get_identity),
    service: ContratoService = Depends(get_contrato_service),
):
    """
    Deleta um contrato específico.
    
    Requer autenticação (JWT Bearer token) e roles: revisor ou admin.
    
    ### Parâmetros:
    - **contrato_id**: ID do contrato a deletar
    
    ### Response:
    - 204: Deletado com sucesso (sem corpo)
    
    ### Erros:
    - 404: Contrato não encontrado
    - 403: Você não tem permissão para deletar este contrato
    """
    
    contrato = service.get_contrato(contrato_id)
    
    if not contrato:
        raise ContratoNaoEncontrado(contrato_id)
    
    # Validar tenant_id (multi-tenancy isolation)
    if contrato.tenant_id != identity.tenant_id:
        raise SemPermissao("Este contrato não pertence ao seu tenant")
    
    service.delete_contrato(contrato_id)

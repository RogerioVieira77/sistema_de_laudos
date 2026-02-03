"""
Contratos Router - API endpoints for contract management
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.api.dependencies import get_db, get_current_user
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
        500: {"description": "Erro ao extrair dados do PDF"},
    }
)
async def upload_contrato(
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
    current_user_id: int = Depends(get_current_user),
    service: ContratoService = Depends(get_contrato_service),
):
    """
    Faz upload de um contrato em formato PDF.
    
    ### Fluxo:
    1. Valida arquivo (tipo, tamanho)
    2. Salva arquivo no servidor
    3. Extrai dados (CPF, número, coordenadas)
    4. Salva em dados_contrato
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
        upload_dir = "/uploads/contratos"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{current_user_id}_{numero_contrato}.pdf")
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Criar contrato no banco
        contrato_data = DadosContratoCreate(
            usuario_id=current_user_id,
            numero_contrato=numero_contrato,
            cpf_cliente=cpf_limpo,
            endereco_assinatura="Extraído do PDF",
            arquivo_pdf_path=file_path,
            latitude=None,  # TODO: Extrair do PDF
            longitude=None,  # TODO: Extrair do PDF
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
    }
)
async def get_contrato(
    contrato_id: int,
    current_user_id: int = Depends(get_current_user),
    service: ContratoService = Depends(get_contrato_service),
):
    """
    Obtém um contrato específico.
    
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
    
    if contrato.usuario_id != current_user_id:
        raise SemPermissao("Este contrato não pertence ao seu usuário")
    
    return contrato


@router.get(
    "",
    summary="Listar Contratos",
    description="Lista todos os contratos do usuário com paginação",
    responses={
        200: {"description": "Lista de contratos"},
    }
)
async def list_contratos(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(10, ge=1, le=100, description="Número de registros a retornar"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    current_user_id: int = Depends(get_current_user),
    service: ContratoService = Depends(get_contrato_service),
):
    """
    Lista todos os contratos do usuário autenticado.
    
    ### Parâmetros:
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Número de registros a retornar (padrão: 10, máx: 100)
    - **status**: Filtrar por status (opcional)
    
    ### Response:
    - **total**: Total de contratos
    - **skip**: Página atual
    - **limit**: Registros por página
    - **contratos**: Lista de contratos
    """
    
    resultado = service.get_contratos_usuario(
        current_user_id,
        skip=skip,
        limit=limit
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
    }
)
async def delete_contrato(
    contrato_id: int,
    current_user_id: int = Depends(get_current_user),
    service: ContratoService = Depends(get_contrato_service),
):
    """
    Deleta um contrato específico.
    
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
    
    if contrato.usuario_id != current_user_id:
        raise SemPermissao("Você não tem permissão para deletar este contrato")
    
    service.delete_contrato(contrato_id)

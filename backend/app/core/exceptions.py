"""
Custom Exception Classes for API
Organized by domain and HTTP status code
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class APIException(HTTPException):
    """
    Base class for all API exceptions.
    Extends FastAPI HTTPException with additional context.
    """
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


# ============================================================================
# 404 NOT FOUND EXCEPTIONS
# ============================================================================

class ContratoNaoEncontrado(APIException):
    """Contrato não encontrado no banco de dados"""
    
    def __init__(self, contrato_id: int = None):
        detail = "Contrato não encontrado"
        if contrato_id:
            detail += f" (ID: {contrato_id})"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class BureauNaoEncontrado(APIException):
    """Dados de Bureau não encontrados"""
    
    def __init__(self, contrato_id: int = None):
        detail = "Dados de Bureau não encontrados"
        if contrato_id:
            detail += f" para contrato ID: {contrato_id}"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class PareceNaoEncontrado(APIException):
    """Parecer não encontrado no banco de dados"""
    
    def __init__(self, parecer_id: int = None):
        detail = "Parecer não encontrado"
        if parecer_id:
            detail += f" (ID: {parecer_id})"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class UsuarioNaoEncontrado(APIException):
    """Usuário não encontrado"""
    
    def __init__(self, usuario_id: int = None):
        detail = "Usuário não encontrado"
        if usuario_id:
            detail += f" (ID: {usuario_id})"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


# ============================================================================
# 400 BAD REQUEST EXCEPTIONS
# ============================================================================

class ArquivoInvalido(APIException):
    """Arquivo fornecido é inválido"""
    
    def __init__(self, reason: str = "Arquivo PDF inválido"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo inválido: {reason}",
        )


class ArquivoMuitoGrande(APIException):
    """Arquivo excede o tamanho máximo permitido"""
    
    def __init__(self, max_size_mb: int = 10):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo muito grande. Máximo permitido: {max_size_mb}MB",
        )


class DadosInsuficientes(APIException):
    """Dados insuficientes para realizar a operação"""
    
    def __init__(self, reason: str = "Dados insuficientes"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Dados insuficientes: {reason}",
        )


class ErroExtracao(APIException):
    """Erro ao extrair dados do arquivo PDF"""
    
    def __init__(self, reason: str = "Erro ao extrair dados"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao extrair PDF: {reason}",
        )


# ============================================================================
# 403 FORBIDDEN EXCEPTIONS
# ============================================================================

class SemPermissao(APIException):
    """Usuário não tem permissão para acessar este recurso"""
    
    def __init__(self, reason: str = "Sem permissão"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão: {reason}",
        )


class ContratoJaPertenceAOutroUsuario(APIException):
    """Contrato já pertence a outro usuário"""
    
    def __init__(self, contrato_id: int = None):
        detail = "Este contrato não pertence ao seu usuário"
        if contrato_id:
            detail += f" (ID: {contrato_id})"
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


# ============================================================================
# 422 UNPROCESSABLE ENTITY EXCEPTIONS
# ============================================================================

class ValidacaoFalhou(APIException):
    """Validação de dados falhou"""
    
    def __init__(self, campo: str = None, motivo: str = None):
        detail = "Validação falhou"
        if campo:
            detail = f"Validação falhou no campo '{campo}'"
        if motivo:
            detail += f": {motivo}"
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class CPFInvalido(APIException):
    """CPF fornecido é inválido"""
    
    def __init__(self, cpf: str = None):
        detail = "CPF inválido"
        if cpf:
            detail += f": {cpf}"
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class CEPInvalido(APIException):
    """CEP fornecido é inválido"""
    
    def __init__(self, cep: str = None):
        detail = "CEP inválido"
        if cep:
            detail += f": {cep}"
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class CoordenadasInvalidas(APIException):
    """Coordenadas (latitude/longitude) inválidas"""
    
    def __init__(self, latitude: float = None, longitude: float = None):
        detail = "Coordenadas inválidas"
        if latitude is not None and longitude is not None:
            detail += f" (lat: {latitude}, lng: {longitude})"
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


# ============================================================================
# 503 SERVICE UNAVAILABLE EXCEPTIONS
# ============================================================================

class ServicoGeocodificacaoIndisponivel(APIException):
    """Serviço de geocodificação (Nominatim) está indisponível"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de geocodificação indisponível. Tente novamente mais tarde.",
        )


class BancoDadosIndisponivel(APIException):
    """Banco de dados está indisponível"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados indisponível. Tente novamente mais tarde.",
        )


class ServicoExternoIndisponivel(APIException):
    """Serviço externo (Bureau, Nominatim, etc) está indisponível"""
    
    def __init__(self, servico: str = "Serviço externo"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{servico} indisponível. Tente novamente mais tarde.",
        )


# ============================================================================
# 500 INTERNAL SERVER ERROR EXCEPTIONS
# ============================================================================

class ErroInterno(APIException):
    """Erro interno do servidor"""
    
    def __init__(self, detail: str = "Erro interno do servidor"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class ErroProcessamento(APIException):
    """Erro ao processar dados"""
    
    def __init__(self, operacao: str = "processamento"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao realizar {operacao}. Tente novamente mais tarde.",
        )


# ============================================================================
# Exception Handler Registration
# To be used in main.py:
#
# from fastapi import FastAPI
# from app.core.exceptions import APIException
#
# app = FastAPI()
#
# @app.exception_handler(APIException)
# async def api_exception_handler(request, exc):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail},
#     )
# ============================================================================

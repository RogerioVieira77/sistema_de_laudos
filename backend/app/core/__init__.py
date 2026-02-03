"""
Core Module - Core functionality and utilities
"""

from .exceptions import (
    APIException,
    ContratoNaoEncontrado,
    BureauNaoEncontrado,
    PareceNaoEncontrado,
    UsuarioNaoEncontrado,
    ArquivoInvalido,
    ArquivoMuitoGrande,
    DadosInsuficientes,
    ErroExtracao,
    SemPermissao,
    ContratoJaPertenceAOutroUsuario,
    ValidacaoFalhou,
    CPFInvalido,
    CEPInvalido,
    CoordenadasInvalidas,
    ServicoGeocodificacaoIndisponivel,
    BancoDadosIndisponivel,
    ServicoExternoIndisponivel,
    ErroInterno,
    ErroProcessamento,
)

__all__ = [
    "APIException",
    "ContratoNaoEncontrado",
    "BureauNaoEncontrado",
    "PareceNaoEncontrado",
    "UsuarioNaoEncontrado",
    "ArquivoInvalido",
    "ArquivoMuitoGrande",
    "DadosInsuficientes",
    "ErroExtracao",
    "SemPermissao",
    "ContratoJaPertenceAOutroUsuario",
    "ValidacaoFalhou",
    "CPFInvalido",
    "CEPInvalido",
    "CoordenadasInvalidas",
    "ServicoGeocodificacaoIndisponivel",
    "BancoDadosIndisponivel",
    "ServicoExternoIndisponivel",
    "ErroInterno",
    "ErroProcessamento",
]

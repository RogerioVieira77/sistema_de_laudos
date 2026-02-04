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

from .oidc_provider import (
    OIDCProvider,
    KeycloakProvider,
    MicrosoftEntraProvider,
    GoogleProvider,
    AWSCognitoProvider,
    OIDCProviderFactory,
    ProviderType,
    get_provider,
    set_provider,
)

from .oidc_models import (
    OIDCConfig,
    Identity,
    TokenValidationResult,
    IdentityAdapter,
    JWKSCache,
)

__all__ = [
    # Exceptions
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
    # OIDC
    "OIDCProvider",
    "KeycloakProvider",
    "MicrosoftEntraProvider",
    "GoogleProvider",
    "AWSCognitoProvider",
    "OIDCProviderFactory",
    "ProviderType",
    "get_provider",
    "set_provider",
    "OIDCConfig",
    "Identity",
    "TokenValidationResult",
    "IdentityAdapter",
    "JWKSCache",
]

"""
Pydantic Schemas (DTOs) for API validation
"""

# Usuario Schemas
from .usuario_schema import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioListResponse,
)

# Contrato Schemas
from .contrato_schema import (
    DadosContratoBase,
    DadosContratoCreate,
    DadosContratoUpdate,
    DadosContratoResponse,
    DadosContratoListResponse,
)

# Bureau Schemas
from .bureau_schema import (
    DadosBureauBase,
    DadosBureauCreate,
    DadosBureauUpdate,
    DadosBureauResponse,
    DadosBureauListResponse,
)

# Parecer Schemas
from .parecer_schema import (
    PareceBase,
    PareceCreate,
    PareceUpdate,
    PareceResponse,
    PareceListResponse,
    PareceFilterRequest,
)

# Geolocation Schemas
from .geolocation_schema import (
    GeolocationRequest,
    GeolocationAnalysisResponse,
    CoordenadasRequest,
    DistanceCalculationRequest,
    DistanceCalculationResponse,
)

# Logs Schemas
from .logs_schema import (
    LogsAnaliseBase,
    LogsAnaliseCreate,
    LogsAnaliseResponse,
    LogsAnaliseListResponse,
    LogsAnaliseFilterRequest,
)

__all__ = [
    # Usuario
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioResponse",
    "UsuarioListResponse",
    # Contrato
    "DadosContratoBase",
    "DadosContratoCreate",
    "DadosContratoUpdate",
    "DadosContratoResponse",
    "DadosContratoListResponse",
    # Bureau
    "DadosBureauBase",
    "DadosBureauCreate",
    "DadosBureauUpdate",
    "DadosBureauResponse",
    "DadosBureauListResponse",
    # Parecer
    "PareceBase",
    "PareceCreate",
    "PareceUpdate",
    "PareceResponse",
    "PareceListResponse",
    "PareceFilterRequest",
    # Geolocation
    "GeolocationRequest",
    "GeolocationAnalysisResponse",
    "CoordenadasRequest",
    "DistanceCalculationRequest",
    "DistanceCalculationResponse",
    # Logs
    "LogsAnaliseBase",
    "LogsAnaliseCreate",
    "LogsAnaliseResponse",
    "LogsAnaliseListResponse",
    "LogsAnaliseFilterRequest",
]


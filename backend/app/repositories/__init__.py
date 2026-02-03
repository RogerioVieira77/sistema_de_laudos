"""
Repository Pattern - Data Access Layer
All repositories for database operations
"""

from .base_repository import BaseRepository
from .usuario_repository import UsuarioRepository
from .contrato_repository import ContratoRepository
from .bureau_repository import BureauRepository
from .parecer_repository import PareceRepository
from .logs_repository import LogsAnaliseRepository

__all__ = [
    "BaseRepository",
    "UsuarioRepository",
    "ContratoRepository",
    "BureauRepository",
    "PareceRepository",
    "LogsAnaliseRepository",
]

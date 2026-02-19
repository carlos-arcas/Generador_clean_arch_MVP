"""DTOs para auditorías de aplicación."""

from .dto_auditoria_finalizacion_entrada import DtoAuditoriaFinalizacionEntrada
from .dto_auditoria_finalizacion_salida import (
    ConflictosFinalizacion,
    DtoAuditoriaFinalizacionSalida,
    ResultadoEtapa,
)

__all__ = [
    "DtoAuditoriaFinalizacionEntrada",
    "DtoAuditoriaFinalizacionSalida",
    "ResultadoEtapa",
    "ConflictosFinalizacion",
]

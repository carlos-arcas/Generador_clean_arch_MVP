"""DTOs para auditorías de aplicación."""

from .dto_auditoria_finalizacion_entrada import DtoAuditoriaFinalizacionEntrada
from .dto_auditoria_finalizacion_salida import (
    ConflictosFinalizacion,
    DtoAuditoriaFinalizacionSalida,
    ResultadoEtapa,
)
from .tipos_fallo import CONFLICTO, INESPERADO, IO, VALIDACION
from .dto_informe_finalizacion import (
    DtoConflictosRutasInforme,
    DtoErrorTecnicoInforme,
    DtoEtapaInforme,
    DtoInformeFinalizacion,
    EvidenciasCompat,
)

__all__ = [
    "DtoAuditoriaFinalizacionEntrada",
    "DtoAuditoriaFinalizacionSalida",
    "ResultadoEtapa",
    "ConflictosFinalizacion",
    "VALIDACION",
    "CONFLICTO",
    "IO",
    "INESPERADO",
    "DtoInformeFinalizacion",
    "DtoEtapaInforme",
    "DtoConflictosRutasInforme",
    "DtoErrorTecnicoInforme",
    "EvidenciasCompat",
]

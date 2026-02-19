"""Taxonomía de errores de la capa de aplicación."""

from .errores_auditoria import ErrorAuditoria
from .errores_generacion import (
    ErrorBlueprintNoEncontrado,
    ErrorConflictoArchivos,
    ErrorGeneracionProyecto,
    ErrorInfraestructura,
)
from .errores_pipeline import (
    ErrorAuditoriaGeneracion,
    ErrorEjecucionPlanGeneracion,
    ErrorNormalizacionEntradaGeneracion,
    ErrorPreparacionEstructuraGeneracion,
    ErrorPublicacionManifestGeneracion,
    ErrorValidacionEntradaGeneracion,
)
from .errores_validacion import ErrorAplicacion, ErrorValidacion, ErrorValidacionEntrada

__all__ = [
    "ErrorAplicacion",
    "ErrorAuditoria",
    "ErrorAuditoriaGeneracion",
    "ErrorBlueprintNoEncontrado",
    "ErrorConflictoArchivos",
    "ErrorEjecucionPlanGeneracion",
    "ErrorGeneracionProyecto",
    "ErrorInfraestructura",
    "ErrorNormalizacionEntradaGeneracion",
    "ErrorPreparacionEstructuraGeneracion",
    "ErrorPublicacionManifestGeneracion",
    "ErrorValidacion",
    "ErrorValidacionEntrada",
    "ErrorValidacionEntradaGeneracion",
]

"""DEPRECADO — eliminar en siguiente iteración.

Reexporta modelos de dominio para mantener compatibilidad temporal.
"""

from dominio.especificacion import (
    ErrorValidacionDominio,
    EspecificacionAtributo,
    EspecificacionClase,
    EspecificacionProyecto,
)
from dominio.manifest import EntradaManifest, ManifestProyecto
from dominio.plan_generacion import ArchivoGenerado, PlanGeneracion

__all__ = [
    "ArchivoGenerado",
    "EntradaManifest",
    "ErrorValidacionDominio",
    "EspecificacionAtributo",
    "EspecificacionClase",
    "EspecificacionProyecto",
    "ManifestProyecto",
    "PlanGeneracion",
]

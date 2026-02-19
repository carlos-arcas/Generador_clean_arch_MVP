"""Compatibilidad de errores del pipeline (re-export desde aplicacion.errores)."""

from __future__ import annotations

from aplicacion.errores import (
    ErrorAuditoriaGeneracion,
    ErrorEjecucionPlanGeneracion,
    ErrorNormalizacionEntradaGeneracion,
    ErrorPreparacionEstructuraGeneracion,
    ErrorPublicacionManifestGeneracion,
    ErrorValidacionEntradaGeneracion,
)

__all__ = [
    "ErrorAuditoriaGeneracion",
    "ErrorEjecucionPlanGeneracion",
    "ErrorNormalizacionEntradaGeneracion",
    "ErrorPreparacionEstructuraGeneracion",
    "ErrorPublicacionManifestGeneracion",
    "ErrorValidacionEntradaGeneracion",
]

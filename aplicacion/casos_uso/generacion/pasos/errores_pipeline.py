"""Errores tipados para el pipeline de generación MVP."""

from __future__ import annotations

from aplicacion.errores import ErrorAplicacion


class ErrorValidacionEntradaGeneracion(ErrorAplicacion):
    """Error en validación de entrada del pipeline."""


class ErrorNormalizacionEntradaGeneracion(ErrorAplicacion):
    """Error al normalizar los datos de entrada."""


class ErrorPreparacionEstructuraGeneracion(ErrorAplicacion):
    """Error al preparar carpetas base del proyecto."""


class ErrorEjecucionPlanGeneracion(ErrorAplicacion):
    """Error al crear o ejecutar el plan de archivos."""


class ErrorPublicacionManifestGeneracion(ErrorAplicacion):
    """Error durante la publicación del manifest del proyecto."""


class ErrorAuditoriaGeneracion(ErrorAplicacion):
    """Error durante la auditoría del proyecto generado."""

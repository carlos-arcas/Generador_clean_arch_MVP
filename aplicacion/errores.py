"""Excepciones de aplicación del generador."""

from __future__ import annotations


class ErrorAplicacion(Exception):
    """Base para errores de la capa de aplicación."""


class ErrorValidacion(ErrorAplicacion):
    """Error de validación de datos o contratos de entrada."""


class ErrorConflictoArchivos(ErrorAplicacion):
    """Error por conflictos de rutas o estado de archivos."""


class ErrorAuditoria(ErrorAplicacion):
    """Error al ejecutar o consolidar la auditoría."""


class ErrorBlueprintNoEncontrado(ErrorAplicacion):
    """Error cuando no existe el blueprint solicitado."""

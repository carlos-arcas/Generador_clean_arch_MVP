"""Excepciones de aplicación del generador."""

from __future__ import annotations


class ErrorAplicacion(Exception):
    """Base para errores de la capa de aplicación."""


class ErrorValidacionEntrada(ErrorAplicacion):
    """Error de validación de datos o contratos de entrada."""


class ErrorValidacion(ErrorValidacionEntrada):
    """Alias compatible para validaciones de entrada en aplicación."""


class ErrorGeneracionProyecto(ErrorAplicacion):
    """Error funcional al orquestar la generación de un proyecto."""


class ErrorConflictoArchivos(ErrorAplicacion):
    """Error por conflictos de rutas o estado de archivos."""


class ErrorAuditoria(ErrorAplicacion):
    """Error al ejecutar o consolidar la auditoría."""


class ErrorBlueprintNoEncontrado(ErrorAplicacion):
    """Error cuando no existe el blueprint solicitado."""


class ErrorInfraestructura(ErrorAplicacion):
    """Error técnico proveniente de un adaptador de infraestructura."""

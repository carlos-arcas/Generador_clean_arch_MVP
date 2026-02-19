"""Taxonomía de errores de infraestructura."""

from __future__ import annotations

from aplicacion.errores import ErrorInfraestructura


class ErrorFilesystem(ErrorInfraestructura):
    """Fallo al interactuar con sistema de archivos."""


class ErrorSubproceso(ErrorInfraestructura):
    """Fallo al ejecutar procesos externos."""

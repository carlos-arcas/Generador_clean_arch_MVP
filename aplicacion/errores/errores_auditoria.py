"""Errores relacionados con la auditoría de proyectos generados."""

from __future__ import annotations

from .errores_validacion import ErrorAplicacion


class ErrorAuditoria(ErrorAplicacion):
    """Error al ejecutar o consolidar la auditoría."""

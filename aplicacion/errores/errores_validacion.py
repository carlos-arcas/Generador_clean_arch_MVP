"""Errores relacionados con validaciones de entrada en aplicación."""

from __future__ import annotations


class ErrorAplicacion(Exception):
    """Base para errores de la capa de aplicación."""


class ErrorValidacionEntrada(ErrorAplicacion):
    """Error de validación de datos o contratos de entrada."""


class ErrorValidacion(ErrorValidacionEntrada):
    """Alias compatible para validaciones de entrada en aplicación."""

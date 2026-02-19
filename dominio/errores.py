"""Taxonomía de errores de la capa de dominio."""

from __future__ import annotations


class ErrorDominio(Exception):
    """Error base para reglas y modelos de dominio."""


class ErrorValidacionDominio(ValueError, ErrorDominio):
    """Error de validación funcional de entidades o value objects."""


class ErrorInvarianteDominio(ErrorDominio):
    """Error cuando una invariante de dominio no se cumple."""


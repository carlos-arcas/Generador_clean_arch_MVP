"""Excepción de dominio para proteger sobreescritura de proyectos."""

from __future__ import annotations


from dominio.errores import ErrorInvarianteDominio


class ProyectoYaExisteError(ErrorInvarianteDominio):
    """Se lanza cuando la carpeta destino del proyecto ya contiene archivos."""

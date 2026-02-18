"""Excepción de dominio para proteger sobreescritura de proyectos."""

from __future__ import annotations


class ProyectoYaExisteError(Exception):
    """Se lanza cuando la carpeta destino del proyecto ya contiene archivos."""

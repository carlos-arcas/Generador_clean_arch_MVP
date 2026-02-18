"""Compatibilidad con el composition root histórico."""

from __future__ import annotations

from infraestructura.bootstrap import (  # noqa: F401
    ContenedorAplicacion,
    configurar_logging,
    construir_contenedor_aplicacion,
)


def crear_contenedor() -> ContenedorAplicacion:
    """Alias histórico para mantener compatibilidad."""

    return construir_contenedor_aplicacion()


__all__ = [
    "ContenedorAplicacion",
    "crear_contenedor",
    "construir_contenedor_aplicacion",
    "configurar_logging",
]

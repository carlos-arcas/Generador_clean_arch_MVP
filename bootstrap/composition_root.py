"""Compatibilidad con el composition root histórico."""

from __future__ import annotations

from infraestructura.bootstrap import (  # noqa: F401
    ContenedorAplicacion,
    ContenedorCli,
    ContenedorGui,
    configurar_logging,
    construir_contenedor_aplicacion,
    construir_contenedor_cli,
    construir_contenedor_gui,
)


def crear_contenedor() -> ContenedorAplicacion:
    """Alias histórico para mantener compatibilidad."""

    return construir_contenedor_aplicacion()


__all__ = [
    "ContenedorAplicacion",
    "ContenedorCli",
    "ContenedorGui",
    "crear_contenedor",
    "construir_contenedor_aplicacion",
    "construir_contenedor_cli",
    "construir_contenedor_gui",
    "configurar_logging",
]

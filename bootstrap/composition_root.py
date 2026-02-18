"""Compatibilidad del composition root histórico."""

from __future__ import annotations

from infraestructura.bootstrap import (
    ContenedorAplicacion,
    configurar_logging,
    construir_contenedor_aplicacion,
)


def crear_contenedor() -> ContenedorAplicacion:
    """Alias histórico hacia el nuevo bootstrap de infraestructura."""

    return construir_contenedor_aplicacion()


__all__ = ["ContenedorAplicacion", "crear_contenedor", "configurar_logging"]

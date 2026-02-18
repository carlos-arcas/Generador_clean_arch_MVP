"""Puerto para descubrimiento y carga de plugins de blueprints."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from aplicacion.puertos.blueprint import Blueprint


class DescubridorPluginsPuerto(Protocol):
    """Contrato para explorar y cargar plugins externos."""

    def descubrir(self, ruta: Path) -> list[Blueprint]:
        """Descubre plugins disponibles en una ruta determinada."""

    def cargar_plugin(self, nombre: str) -> Blueprint:
        """Carga un plugin por nombre lógico."""


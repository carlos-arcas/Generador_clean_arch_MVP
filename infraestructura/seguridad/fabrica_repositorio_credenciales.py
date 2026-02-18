"""Fábrica de repositorio de credenciales por plataforma."""

from __future__ import annotations

import logging
import sys

from aplicacion.casos_uso.seguridad import RepositorioCredenciales

from .repositorio_credenciales_memoria import RepositorioCredencialesMemoria
from .repositorio_credenciales_windows import RepositorioCredencialesWindows

LOGGER = logging.getLogger(__name__)


class SelectorRepositorioCredenciales:
    """Selecciona repositorio seguro por defecto."""

    def crear(self) -> RepositorioCredenciales:
        if sys.platform.startswith("win"):
            try:
                return RepositorioCredencialesWindows()
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning(
                    "No se pudo iniciar almacenamiento seguro de Windows; se usará memoria temporal. %s",
                    exc,
                )
        return RepositorioCredencialesMemoria()

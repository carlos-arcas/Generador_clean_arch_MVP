"""Fábrica de repositorio de credenciales por plataforma."""

from __future__ import annotations

import logging
import sys

from aplicacion.errores import ErrorInfraestructura
from aplicacion.casos_uso.seguridad import RepositorioCredenciales

from .repositorio_credenciales_memoria import RepositorioCredencialesMemoria
from .repositorio_credenciales_windows import RepositorioCredencialesWindows

LOGGER = logging.getLogger(__name__)


class SelectorRepositorioCredenciales:
    """Selecciona repositorio seguro por defecto."""

    def _crear_repositorio_windows(self) -> RepositorioCredenciales:
        try:
            return RepositorioCredencialesWindows()
        except (OSError, IOError, PermissionError, ValueError) as exc:
            raise ErrorInfraestructura(
                "No se pudo iniciar almacenamiento seguro de Windows."
            ) from exc

    def crear(self) -> RepositorioCredenciales:
        if sys.platform.startswith("win"):
            try:
                return self._crear_repositorio_windows()
            except ErrorInfraestructura as exc:
                LOGGER.warning(
                    "No se pudo iniciar almacenamiento seguro de Windows; se usará memoria temporal.",
                    exc_info=True,
                )
        return RepositorioCredencialesMemoria()

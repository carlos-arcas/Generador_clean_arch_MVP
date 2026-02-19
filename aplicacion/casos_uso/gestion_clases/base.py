"""Utilidades compartidas para casos de uso de gestión de clases."""

from __future__ import annotations

from aplicacion.puertos.repositorio_especificacion_proyecto import RepositorioEspecificacionProyecto


class CasoUsoGestionClases:
    """Base para inyectar el repositorio de especificación."""

    def __init__(self, repositorio: RepositorioEspecificacionProyecto) -> None:
        self._repositorio = repositorio

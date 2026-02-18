"""Repositorio en memoria para la especificación del proyecto."""

from __future__ import annotations

from aplicacion.puertos.repositorio_especificacion_proyecto import (
    RepositorioEspecificacionProyecto,
)
from dominio.modelos import EspecificacionProyecto


class RepositorioEspecificacionProyectoEnMemoria(RepositorioEspecificacionProyecto):
    """Implementación en memoria orientada a pruebas."""

    def __init__(self, especificacion_inicial: EspecificacionProyecto | None = None) -> None:
        self._especificacion = especificacion_inicial or EspecificacionProyecto(
            nombre_proyecto="proyecto_en_memoria",
            ruta_destino="/tmp/proyecto_en_memoria",
            version="0.1.0",
        )

    def obtener(self) -> EspecificacionProyecto:
        return self._especificacion

    def guardar(self, especificacion: EspecificacionProyecto) -> None:
        self._especificacion = especificacion

"""Casos de uso para bajas de clases y atributos."""

from __future__ import annotations

import logging

from aplicacion.casos_uso.gestion_clases.base import CasoUsoGestionClases
from dominio.especificacion import ErrorValidacionDominio

logger = logging.getLogger(__name__)


class EliminarClase(CasoUsoGestionClases):
    def ejecutar(self, id_clase: str) -> None:
        logger.debug("Intentando eliminar clase con id '%s'.", id_clase)
        especificacion = self._repositorio.obtener()
        try:
            especificacion.eliminar_clase(id_clase)
        except ErrorValidacionDominio:
            logger.warning("No se pudo eliminar la clase id '%s'.", id_clase)
            raise
        self._repositorio.guardar(especificacion)
        logger.info("Clase eliminada con id '%s'.", id_clase)


class EliminarAtributo(CasoUsoGestionClases):
    def ejecutar(self, id_clase: str, id_atributo: str) -> None:
        logger.debug(
            "Intentando eliminar atributo id '%s' en clase id '%s'.", id_atributo, id_clase
        )
        especificacion = self._repositorio.obtener()
        try:
            clase = especificacion.obtener_clase(id_clase)
            clase.eliminar_atributo(id_atributo)
        except ErrorValidacionDominio:
            logger.warning(
                "No se pudo eliminar atributo id '%s' en clase id '%s'.",
                id_atributo,
                id_clase,
            )
            raise
        self._repositorio.guardar(especificacion)
        logger.info("Atributo id '%s' eliminado en clase id '%s'.", id_atributo, id_clase)

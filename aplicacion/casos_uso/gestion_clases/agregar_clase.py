"""Casos de uso para altas de clases y atributos."""

from __future__ import annotations

import logging

from aplicacion.casos_uso.gestion_clases.base import CasoUsoGestionClases
from dominio.especificacion import ErrorValidacionDominio, EspecificacionAtributo, EspecificacionClase

logger = logging.getLogger(__name__)


class AgregarClase(CasoUsoGestionClases):
    def ejecutar(self, clase: EspecificacionClase) -> EspecificacionClase:
        logger.debug("Intentando agregar clase '%s'.", clase.nombre)
        especificacion = self._repositorio.obtener()
        try:
            especificacion.agregar_clase(clase)
        except ErrorValidacionDominio:
            logger.warning("No se pudo agregar clase '%s'.", clase.nombre)
            raise
        self._repositorio.guardar(especificacion)
        logger.info("Clase agregada: '%s'.", clase.nombre)
        return clase


class AgregarAtributo(CasoUsoGestionClases):
    def ejecutar(self, id_clase: str, atributo: EspecificacionAtributo) -> EspecificacionAtributo:
        logger.debug(
            "Intentando agregar atributo '%s' a clase id '%s'.", atributo.nombre, id_clase
        )
        especificacion = self._repositorio.obtener()
        try:
            clase = especificacion.obtener_clase(id_clase)
            clase.agregar_atributo(atributo)
        except ErrorValidacionDominio:
            logger.warning(
                "No se pudo agregar atributo '%s' a clase id '%s'.",
                atributo.nombre,
                id_clase,
            )
            raise
        self._repositorio.guardar(especificacion)
        logger.info("Atributo '%s' agregado a clase id '%s'.", atributo.nombre, id_clase)
        return atributo

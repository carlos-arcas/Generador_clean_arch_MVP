"""Casos de uso para modificaciones de clases y atributos."""

from __future__ import annotations

import logging

from aplicacion.casos_uso.gestion_clases.base import CasoUsoGestionClases
from dominio.especificacion import ErrorValidacionDominio, EspecificacionAtributo, EspecificacionClase

logger = logging.getLogger(__name__)


class RenombrarClase(CasoUsoGestionClases):
    def ejecutar(self, id_clase: str, nuevo_nombre: str) -> EspecificacionClase:
        logger.debug("Intentando renombrar clase id '%s' a '%s'.", id_clase, nuevo_nombre)
        especificacion = self._repositorio.obtener()
        try:
            clase = especificacion.renombrar_clase(id_clase, nuevo_nombre)
        except ErrorValidacionDominio:
            logger.warning(
                "No se pudo renombrar la clase id '%s' a '%s'.", id_clase, nuevo_nombre
            )
            raise
        self._repositorio.guardar(especificacion)
        logger.info("Clase '%s' renombrada a '%s'.", id_clase, nuevo_nombre)
        return clase


class EditarAtributo(CasoUsoGestionClases):
    def ejecutar(
        self,
        id_clase: str,
        id_atributo: str,
        nombre: str,
        tipo: str,
        obligatorio: bool,
        valor_por_defecto: str | None,
    ) -> EspecificacionAtributo:
        logger.debug(
            "Intentando editar atributo id '%s' en clase id '%s'.", id_atributo, id_clase
        )
        especificacion = self._repositorio.obtener()
        try:
            clase = especificacion.obtener_clase(id_clase)
            atributo = clase.editar_atributo(
                id_interno=id_atributo,
                nombre=nombre,
                tipo=tipo,
                obligatorio=obligatorio,
                valor_por_defecto=valor_por_defecto,
            )
        except ErrorValidacionDominio:
            logger.warning(
                "No se pudo editar atributo id '%s' en clase id '%s'.",
                id_atributo,
                id_clase,
            )
            raise
        self._repositorio.guardar(especificacion)
        logger.info("Atributo id '%s' editado en clase id '%s'.", id_atributo, id_clase)
        return atributo

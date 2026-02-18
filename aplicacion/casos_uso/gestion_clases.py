"""Casos de uso para gestionar clases y atributos del constructor dinámico."""

from __future__ import annotations

import logging

from aplicacion.puertos.repositorio_especificacion_proyecto import (
    RepositorioEspecificacionProyecto,
)
from dominio.especificacion import ErrorValidacionDominio, EspecificacionAtributo, EspecificacionClase

logger = logging.getLogger(__name__)


class AgregarClase:
    def __init__(self, repositorio: RepositorioEspecificacionProyecto) -> None:
        self._repositorio = repositorio

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


class EliminarClase:
    def __init__(self, repositorio: RepositorioEspecificacionProyecto) -> None:
        self._repositorio = repositorio

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


class RenombrarClase:
    def __init__(self, repositorio: RepositorioEspecificacionProyecto) -> None:
        self._repositorio = repositorio

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


class AgregarAtributo:
    def __init__(self, repositorio: RepositorioEspecificacionProyecto) -> None:
        self._repositorio = repositorio

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


class EditarAtributo:
    def __init__(self, repositorio: RepositorioEspecificacionProyecto) -> None:
        self._repositorio = repositorio

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


class EliminarAtributo:
    def __init__(self, repositorio: RepositorioEspecificacionProyecto) -> None:
        self._repositorio = repositorio

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


class ListarClases:
    def __init__(self, repositorio: RepositorioEspecificacionProyecto) -> None:
        self._repositorio = repositorio

    def ejecutar(self) -> list[EspecificacionClase]:
        logger.debug("Listando clases actuales del proyecto.")
        clases = self._repositorio.obtener().listar_clases()
        logger.info("Se listaron %s clases.", len(clases))
        return clases


class ObtenerClaseDetallada:
    def __init__(self, repositorio: RepositorioEspecificacionProyecto) -> None:
        self._repositorio = repositorio

    def ejecutar(self, id_clase: str) -> EspecificacionClase:
        logger.debug("Obteniendo detalle de clase id '%s'.", id_clase)
        try:
            clase = self._repositorio.obtener().obtener_clase(id_clase)
        except ErrorValidacionDominio:
            logger.warning("No se pudo obtener detalle de clase id '%s'.", id_clase)
            raise
        logger.info("Detalle obtenido para clase id '%s'.", id_clase)
        return clase

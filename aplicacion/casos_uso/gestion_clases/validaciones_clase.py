"""Consultas y validaciones para gestión de clases."""

from __future__ import annotations

import logging

from aplicacion.casos_uso.gestion_clases.base import CasoUsoGestionClases
from dominio.especificacion import ErrorValidacionDominio, EspecificacionClase

logger = logging.getLogger(__name__)


class ListarClases(CasoUsoGestionClases):
    def ejecutar(self) -> list[EspecificacionClase]:
        logger.debug("Listando clases actuales del proyecto.")
        clases = self._repositorio.obtener().listar_clases()
        logger.info("Se listaron %s clases.", len(clases))
        return clases


class ObtenerClaseDetallada(CasoUsoGestionClases):
    def ejecutar(self, id_clase: str) -> EspecificacionClase:
        logger.debug("Obteniendo detalle de clase id '%s'.", id_clase)
        try:
            clase = self._repositorio.obtener().obtener_clase(id_clase)
        except ErrorValidacionDominio:
            logger.warning("No se pudo obtener detalle de clase id '%s'.", id_clase)
            raise
        logger.info("Detalle obtenido para clase id '%s'.", id_clase)
        return clase

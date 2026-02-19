"""Comando CLI para ejecutar auditoría E2E de finalización."""

from __future__ import annotations

import argparse
import logging
from typing import Any

from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionEntrada
from aplicacion.errores import ErrorValidacionEntrada

LOGGER = logging.getLogger(__name__)


def ejecutar_comando_auditar_finalizacion(args: argparse.Namespace, contenedor_cli: Any) -> int:
    entrada = DtoAuditoriaFinalizacionEntrada(
        ruta_preset=args.preset,
        ruta_salida_auditoria=args.salida,
    )
    salida = contenedor_cli.auditar_finalizacion_proyecto.ejecutar(entrada)

    if not salida.exito_global:
        etapa_conflicto = next((etapa for etapa in salida.etapas if etapa.nombre.startswith("ETAPA 2") and etapa.estado == "FAIL"), None)
        if etapa_conflicto is not None:
            resumen = "\n".join(etapa_conflicto.evidencia[:6])
            raise ErrorValidacionEntrada(f"Conflicto de generación: rutas duplicadas detectadas\n{resumen}")

    LOGGER.info("Auditoría finalización ejecutada id=%s reporte=%s", salida.id_ejecucion, salida.ruta_reporte)
    return 0

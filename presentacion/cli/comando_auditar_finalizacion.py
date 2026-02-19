"""Comando CLI para ejecutar auditoría E2E de finalización."""

from __future__ import annotations

import argparse
import logging

from herramientas.auditar_finalizacion_e2e import ejecutar_auditoria_finalizacion

LOGGER = logging.getLogger(__name__)


def ejecutar_comando_auditar_finalizacion(args: argparse.Namespace, contenedor_cli) -> int:  # type: ignore[no-untyped-def]
    salida = ejecutar_auditoria_finalizacion(
        preset=args.preset,
        sandbox=args.sandbox,
        evidencias=args.evidencias,
        smoke=args.smoke,
        arquitectura=args.arquitectura,
        ejecutor=contenedor_cli.auditar_finalizacion_proyecto.ejecutar,
    )
    LOGGER.info(
        "Auditoría finalización ejecutada id=%s estado=%s codigo=%s",
        salida.id_ejecucion,
        salida.estado_global,
        salida.codigo_fallo,
    )
    return 0

"""Caso de uso para ejecutar un plan de generación de archivos."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from aplicacion.casos_uso.generar_manifest import GenerarManifest
from aplicacion.puertos.sistema_archivos import SistemaArchivos
from dominio.plan_generacion import PlanGeneracion

LOGGER = logging.getLogger(__name__)


class EjecutarPlan:
    """Aplica un plan de generación usando el puerto de sistema de archivos."""

    def __init__(
        self,
        sistema_archivos: SistemaArchivos,
        generador_manifest: GenerarManifest | None = None,
    ) -> None:
        self._sistema_archivos = sistema_archivos
        self._generador_manifest = generador_manifest

    def ejecutar(
        self,
        plan: PlanGeneracion,
        ruta_destino: str,
        opciones: dict[str, Any] | None = None,
        version_generador: str = "0.2.0",
        blueprints_usados: list[str] | None = None,
        generar_manifest: bool = True,
    ) -> list[str]:
        """Crea directorios, escribe archivos y genera el manifest final."""
        plan.validar_sin_conflictos()
        archivos_creados: list[str] = []
        for archivo in plan.archivos:
            LOGGER.info("Generando archivo: %s", archivo.ruta_relativa)
            ruta_absoluta = Path(ruta_destino) / archivo.ruta_relativa
            self._sistema_archivos.asegurar_directorio(str(ruta_absoluta.parent))
            self._sistema_archivos.escribir_texto_atomico(
                str(ruta_absoluta), archivo.contenido_texto
            )
            archivos_creados.append(archivo.ruta_relativa)

        if self._generador_manifest is not None and generar_manifest:
            self._generador_manifest.ejecutar(
                plan=plan,
                ruta_destino=ruta_destino,
                opciones=opciones or {},
                version_generador=version_generador,
                blueprints_usados=blueprints_usados or [],
            )

        return archivos_creados

"""Caso de uso para generar un plan incremental (modo PATCH) desde manifest existente."""

from __future__ import annotations

from dataclasses import replace
import logging
from pathlib import Path

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.puertos.manifest import LectorManifest
from dominio.especificacion import EspecificacionProyecto, ErrorValidacionDominio
from dominio.plan_generacion import PlanGeneracion

LOGGER = logging.getLogger(__name__)


class CrearPlanPatchDesdeBlueprints:
    """Construye un plan parcial únicamente para clases nuevas."""

    def __init__(
        self,
        lector_manifest: LectorManifest,
        crear_plan_desde_blueprints: CrearPlanDesdeBlueprints,
    ) -> None:
        self._lector_manifest = lector_manifest
        self._crear_plan_desde_blueprints = crear_plan_desde_blueprints

    def ejecutar(self, especificacion: EspecificacionProyecto, ruta_proyecto_existente: str) -> PlanGeneracion:
        LOGGER.info("Detección modo PATCH para ruta=%s", ruta_proyecto_existente)
        manifest = self._lector_manifest.leer(ruta_proyecto_existente)
        blueprints = [nombre.split("@", maxsplit=1)[0] for nombre in manifest.blueprints_usados]
        if not blueprints:
            raise ErrorValidacionDominio("El manifest no declara blueprints usados para aplicar PATCH.")

        clases_generadas = set(manifest.obtener_clases_generadas())
        clases_entrantes = {clase.nombre for clase in especificacion.clases}
        clases_repetidas = sorted(clases_generadas.intersection(clases_entrantes))
        if clases_repetidas:
            raise ErrorValidacionDominio(
                f"No se puede aplicar PATCH: ya existen clases generadas: {clases_repetidas}"
            )

        clases_nuevas = [clase for clase in especificacion.clases if clase.nombre not in clases_generadas]
        LOGGER.info("Clases nuevas detectadas para PATCH: %s", [clase.nombre for clase in clases_nuevas])
        if not clases_nuevas:
            return PlanGeneracion()

        especificacion_patch = replace(especificacion, clases=clases_nuevas)
        plan_patch = self._crear_plan_desde_blueprints.ejecutar(especificacion_patch, blueprints)
        rutas_manifest = {entrada.ruta_relativa for entrada in manifest.archivos}
        self._validar_conflictos(plan_patch, ruta_proyecto_existente, rutas_manifest)
        return plan_patch

    def _validar_conflictos(
        self,
        plan: PlanGeneracion,
        ruta_proyecto_existente: str,
        rutas_manifest: set[str],
    ) -> None:
        conflictos: list[str] = []
        base = Path(ruta_proyecto_existente)
        for archivo in plan.archivos:
            if archivo.ruta_relativa in rutas_manifest:
                conflictos.append(f"{archivo.ruta_relativa} (ya registrado en manifest)")
                continue
            if (base / archivo.ruta_relativa).exists():
                conflictos.append(f"{archivo.ruta_relativa} (archivo existente en disco)")
        if conflictos:
            raise ErrorValidacionDominio(
                "Conflicto detectado durante PATCH. Operación abortada: " + "; ".join(conflictos)
            )


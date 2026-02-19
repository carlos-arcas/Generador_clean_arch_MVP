"""Paso para crear y ejecutar el plan de generación de archivos."""

from __future__ import annotations

from dataclasses import dataclass

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.pasos.errores_pipeline import ErrorEjecucionPlanGeneracion
from aplicacion.errores import ErrorAplicacion
from dominio.especificacion import EspecificacionProyecto


@dataclass(frozen=True)
class ResultadoEjecucionPlan:
    """Resultado de creación y ejecución del plan."""

    archivos_creados: list[str]


class EjecutorPlanGeneracion:
    """Compone el plan y lo ejecuta sobre el destino final."""

    def __init__(self, crear_plan: CrearPlanDesdeBlueprints, ejecutar_plan: EjecutarPlan) -> None:
        self._crear_plan = crear_plan
        self._ejecutar_plan = ejecutar_plan

    def ejecutar(
        self,
        especificacion: EspecificacionProyecto,
        blueprints: list[str],
        ruta_proyecto: str,
    ) -> ResultadoEjecucionPlan:
        try:
            plan = self._crear_plan.ejecutar(especificacion, blueprints)
            archivos_creados = self._ejecutar_plan.ejecutar(
                plan=plan,
                ruta_destino=ruta_proyecto,
                opciones={"origen": "wizard_mvp"},
                blueprints_usados=[f"{nombre}@1.0.0" for nombre in blueprints],
                generar_manifest=True,
            )
            return ResultadoEjecucionPlan(archivos_creados=archivos_creados)
        except (ErrorAplicacion, ValueError, FileNotFoundError, OSError, RuntimeError) as exc:
            raise ErrorEjecucionPlanGeneracion("Fallo al ejecutar el plan de generación.") from exc

"""Planificador real de rutas de blueprints sin tocar disco."""

from __future__ import annotations

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.puertos.planificador_blueprint_puerto import PlanificadorBlueprintPuerto
from dominio.especificacion import EspecificacionProyecto


class PlanificadorBlueprintsReal(PlanificadorBlueprintPuerto):
    def __init__(self, crear_plan_desde_blueprints: CrearPlanDesdeBlueprints) -> None:
        self._crear_plan = crear_plan_desde_blueprints

    def obtener_rutas_generadas(self, blueprint_id: str, especificacion: EspecificacionProyecto) -> set[str]:
        plan = self._crear_plan.ejecutar(especificacion, [blueprint_id])
        return set(plan.obtener_rutas())

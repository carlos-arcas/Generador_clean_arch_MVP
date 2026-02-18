"""Implementación del blueprint base clean architecture."""

from __future__ import annotations

from aplicacion.casos_uso.crear_plan_proyecto_base import CrearPlanProyectoBase
from aplicacion.puertos.blueprint import Blueprint
from dominio.modelos import EspecificacionProyecto, PlanGeneracion


class BaseCleanArchBlueprint(Blueprint):
    """Blueprint inicial que reutiliza el caso de uso base existente."""

    def nombre(self) -> str:
        return "base_clean_arch"

    def version(self) -> str:
        return "1.0.0"

    def validar(self, especificacion: EspecificacionProyecto) -> None:
        especificacion.validar()

    def generar_plan(self, especificacion: EspecificacionProyecto) -> PlanGeneracion:
        return CrearPlanProyectoBase().ejecutar(especificacion)

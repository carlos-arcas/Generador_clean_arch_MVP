"""Caso de uso para crear un plan compuesto desde múltiples blueprints."""

from __future__ import annotations

import logging

from aplicacion.errores import ErrorBlueprintNoEncontrado, ErrorConflictoArchivos, ErrorValidacion
from aplicacion.puertos.blueprint import RepositorioBlueprints
from dominio.modelos import ErrorValidacionDominio, EspecificacionProyecto, PlanGeneracion
from infraestructura.plugins.descubridor_plugins import DescubridorPlugins

LOGGER = logging.getLogger(__name__)


class CrearPlanDesdeBlueprints:
    """Compone un plan final a partir de blueprints declarados."""

    def __init__(
        self,
        repositorio_blueprints: RepositorioBlueprints,
        descubridor_plugins: DescubridorPlugins | None = None,
    ) -> None:
        self._repositorio = repositorio_blueprints
        self._descubridor_plugins = descubridor_plugins or DescubridorPlugins()

    def ejecutar(
        self, especificacion: EspecificacionProyecto, nombres_blueprints: list[str]
    ) -> PlanGeneracion:
        """Valida y fusiona planes parciales de blueprints solicitados."""
        plan_final = PlanGeneracion()
        LOGGER.info("Creando plan compuesto con blueprints: %s", nombres_blueprints)

        for nombre_blueprint in nombres_blueprints:
            blueprint = self._resolver_blueprint(nombre_blueprint, nombres_blueprints)

            try:
                blueprint.validar(especificacion)
                plan_blueprint = blueprint.generar_plan(especificacion)
                plan_final = plan_final.fusionar(plan_blueprint)
            except ErrorValidacionDominio as exc:
                if "rutas duplicadas" in str(exc):
                    raise ErrorConflictoArchivos(str(exc)) from exc
                raise ErrorValidacion(str(exc)) from exc

        try:
            plan_final.validar_sin_conflictos()
        except ErrorValidacionDominio as exc:
            raise ErrorConflictoArchivos(str(exc)) from exc
        return plan_final

    def _resolver_blueprint(self, nombre_blueprint: str, seleccionados: list[str]):
        try:
            return self._repositorio.obtener_por_nombre(nombre_blueprint)
        except (ErrorBlueprintNoEncontrado, ValueError):
            LOGGER.info(
                "Blueprint interno '%s' no encontrado, intentando plugins externos.",
                nombre_blueprint,
            )

        try:
            plugin = self._descubridor_plugins.cargar_plugin(nombre_blueprint)
        except ValueError as exc:
            raise ErrorBlueprintNoEncontrado(str(exc)) from exc

        compatibilidades = set(plugin.metadata.compatible_con)
        if compatibilidades and not compatibilidades.intersection(set(seleccionados)):
            raise ErrorValidacion(
                f"Plugin incompatible '{nombre_blueprint}': requiere alguno de {sorted(compatibilidades)}"
            )
        return plugin

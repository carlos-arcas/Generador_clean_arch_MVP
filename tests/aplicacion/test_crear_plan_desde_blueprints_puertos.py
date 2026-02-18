from __future__ import annotations

import pytest

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.errores import ErrorBlueprintNoEncontrado
from aplicacion.puertos.blueprint import Blueprint, RepositorioBlueprints
from dominio.modelos import ArchivoGenerado, EspecificacionProyecto, PlanGeneracion


class BlueprintDoble(Blueprint):
    def __init__(self, nombre_blueprint: str, rutas: list[str]) -> None:
        self._nombre = nombre_blueprint
        self._rutas = rutas

    def nombre(self) -> str:
        return self._nombre

    def version(self) -> str:
        return "1.0.0"

    def validar(self, especificacion: EspecificacionProyecto) -> None:
        especificacion.validar()

    def generar_plan(self, especificacion: EspecificacionProyecto) -> PlanGeneracion:
        return PlanGeneracion([ArchivoGenerado(ruta, "contenido") for ruta in self._rutas])


class RepositorioDoble(RepositorioBlueprints):
    def __init__(self, blueprints: list[Blueprint]) -> None:
        self._blueprints = {blueprint.nombre(): blueprint for blueprint in blueprints}

    def listar_blueprints(self) -> list[Blueprint]:
        return list(self._blueprints.values())

    def obtener_por_nombre(self, nombre: str) -> Blueprint:
        if nombre not in self._blueprints:
            raise ValueError("No encontrado")
        return self._blueprints[nombre]


class DescubridorPluginsFalso:
    def __init__(self, plugins: dict[str, Blueprint] | None = None, error: str | None = None) -> None:
        self._plugins = plugins or {}
        self._error = error

    def descubrir(self, ruta):  # type: ignore[no-untyped-def]
        return list(self._plugins.values())

    def cargar_plugin(self, nombre: str) -> Blueprint:
        if self._error is not None:
            raise ValueError(self._error)
        if nombre not in self._plugins:
            raise ValueError(f"Plugin no encontrado: {nombre}")
        return self._plugins[nombre]


def test_crear_plan_desde_blueprints_usa_plugin_cuando_no_existe_interno() -> None:
    especificacion = EspecificacionProyecto("demo", "/tmp/demo")
    repositorio = RepositorioDoble([])
    descubridor = DescubridorPluginsFalso({"externo": BlueprintDoble("externo", ["docs/guia.md"])})

    plan = CrearPlanDesdeBlueprints(repositorio, descubridor).ejecutar(especificacion, ["externo"])

    assert plan.obtener_rutas() == ["docs/guia.md"]


def test_crear_plan_desde_blueprints_retorna_error_si_falla_puerto_plugins() -> None:
    especificacion = EspecificacionProyecto("demo", "/tmp/demo")
    repositorio = RepositorioDoble([])
    descubridor = DescubridorPluginsFalso(error="fallo de lectura de plugins")

    with pytest.raises(ErrorBlueprintNoEncontrado, match="fallo de lectura"):
        CrearPlanDesdeBlueprints(repositorio, descubridor).ejecutar(especificacion, ["externo"])


def test_crear_plan_desde_blueprints_con_lista_vacia_retorna_plan_vacio() -> None:
    especificacion = EspecificacionProyecto("demo", "/tmp/demo")
    plan = CrearPlanDesdeBlueprints(RepositorioDoble([]), DescubridorPluginsFalso()).ejecutar(
        especificacion,
        [],
    )

    assert plan.obtener_rutas() == []

import pytest

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.puertos.blueprint import Blueprint, RepositorioBlueprints
from dominio.modelos import ArchivoGenerado, EspecificacionProyecto, ErrorValidacionDominio, PlanGeneracion


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
        self._blueprints = {b.nombre(): b for b in blueprints}

    def listar_blueprints(self) -> list[Blueprint]:
        return list(self._blueprints.values())

    def obtener_por_nombre(self, nombre: str) -> Blueprint:
        if nombre not in self._blueprints:
            raise ValueError("No encontrado")
        return self._blueprints[nombre]


def test_crear_plan_desde_blueprints_fusiona_archivos() -> None:
    repo = RepositorioDoble([
        BlueprintDoble("a", ["README.md"]),
        BlueprintDoble("b", ["VERSION"]),
    ])
    especificacion = EspecificacionProyecto("demo", "/tmp/demo")

    plan = CrearPlanDesdeBlueprints(repo).ejecutar(especificacion, ["a", "b"])

    assert plan.obtener_rutas() == ["README.md", "VERSION"]


def test_crear_plan_desde_blueprints_detecta_conflictos() -> None:
    repo = RepositorioDoble([
        BlueprintDoble("a", ["README.md"]),
        BlueprintDoble("b", ["README.md"]),
    ])
    especificacion = EspecificacionProyecto("demo", "/tmp/demo")

    with pytest.raises(ErrorValidacionDominio, match="duplicadas"):
        CrearPlanDesdeBlueprints(repo).ejecutar(especificacion, ["a", "b"])

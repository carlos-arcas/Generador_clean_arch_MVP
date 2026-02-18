import pytest

from blueprints.crud_json_v1.blueprint import CrudJsonBlueprint
from blueprints.crud_sqlite_v1.blueprint import CrudSqliteBlueprint
from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto, ErrorValidacionDominio


def _especificacion_demo() -> EspecificacionProyecto:
    return EspecificacionProyecto(
        nombre_proyecto="demo",
        ruta_destino="/tmp/demo",
        clases=[
            EspecificacionClase(
                nombre="Cliente",
                atributos=[
                    EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True),
                    EspecificacionAtributo(nombre="activo", tipo="bool", obligatorio=True),
                ],
            )
        ],
    )


def test_generar_plan_crud_sqlite_con_una_clase() -> None:
    blueprint = CrudSqliteBlueprint()

    plan = blueprint.generar_plan(_especificacion_demo())
    rutas = set(plan.obtener_rutas())

    assert "infraestructura/persistencia/sqlite/repositorio_cliente_sqlite.py" in rutas
    assert "infraestructura/persistencia/json/repositorio_cliente_json.py" not in rutas
    assert "datos/base_datos.db" not in rutas
    assert "datos/.gitkeep" in rutas

    contenido_repo = next(
        item.contenido_texto
        for item in plan.archivos
        if item.ruta_relativa == "infraestructura/persistencia/sqlite/repositorio_cliente_sqlite.py"
    )
    assert "import sqlite3" in contenido_repo
    assert "base_datos.db" in contenido_repo
    assert "CREATE TABLE IF NOT EXISTS clientes" in contenido_repo
    assert "LOGGER.exception" in contenido_repo


def test_generar_plan_crud_sqlite_reutiliza_dominio_y_aplicacion_de_crud_json() -> None:
    especificacion = _especificacion_demo()

    plan_sqlite = CrudSqliteBlueprint().generar_plan(especificacion)
    plan_json = CrudJsonBlueprint().generar_plan(especificacion)

    rutas_sqlite = {ruta for ruta in plan_sqlite.obtener_rutas() if ruta.startswith(("dominio/", "aplicacion/"))}
    rutas_json = {ruta for ruta in plan_json.obtener_rutas() if ruta.startswith(("dominio/", "aplicacion/"))}

    assert rutas_sqlite == rutas_json


def test_generar_plan_crud_sqlite_sin_clases_falla() -> None:
    blueprint = CrudSqliteBlueprint()
    especificacion = EspecificacionProyecto(nombre_proyecto="demo", ruta_destino="/tmp/demo")

    with pytest.raises(ErrorValidacionDominio, match="al menos una clase"):
        blueprint.generar_plan(especificacion)

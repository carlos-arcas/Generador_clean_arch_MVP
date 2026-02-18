from blueprints.crud_json_v1.blueprint import CrudJsonBlueprint
from blueprints.crud_sqlite_v1.blueprint import CrudSqliteBlueprint
from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto


def _especificacion() -> EspecificacionProyecto:
    return EspecificacionProyecto(
        nombre_proyecto="demo",
        ruta_destino="/tmp/demo",
        clases=[
            EspecificacionClase(
                nombre="Cliente",
                atributos=[
                    EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True),
                    EspecificacionAtributo(nombre="edad", tipo="int", obligatorio=True),
                ],
            )
        ],
    )


def test_intercambiabilidad_dominio_aplicacion_sin_cambios() -> None:
    especificacion = _especificacion()
    plan_json = CrudJsonBlueprint().generar_plan(especificacion)
    plan_sqlite = CrudSqliteBlueprint().generar_plan(especificacion)

    dominio_aplic_json = {
        archivo.ruta_relativa: archivo.contenido_texto
        for archivo in plan_json.archivos
        if archivo.ruta_relativa.startswith(("dominio/", "aplicacion/"))
    }
    dominio_aplic_sqlite = {
        archivo.ruta_relativa: archivo.contenido_texto
        for archivo in plan_sqlite.archivos
        if archivo.ruta_relativa.startswith(("dominio/", "aplicacion/"))
    }

    assert dominio_aplic_sqlite == dominio_aplic_json


def test_intercambiabilidad_cambia_solo_adaptador_infraestructura() -> None:
    especificacion = _especificacion()
    plan_json = CrudJsonBlueprint().generar_plan(especificacion)
    plan_sqlite = CrudSqliteBlueprint().generar_plan(especificacion)

    rutas_json = set(plan_json.obtener_rutas())
    rutas_sqlite = set(plan_sqlite.obtener_rutas())

    assert "infraestructura/persistencia/json/repositorio_cliente_json.py" in rutas_json
    assert "infraestructura/persistencia/sqlite/repositorio_cliente_sqlite.py" in rutas_sqlite
    assert "infraestructura/persistencia/json/repositorio_cliente_json.py" not in rutas_sqlite

    contenido_sqlite = next(
        archivo.contenido_texto
        for archivo in plan_sqlite.archivos
        if archivo.ruta_relativa == "infraestructura/persistencia/sqlite/repositorio_cliente_sqlite.py"
    )
    assert "import sqlite3" in contenido_sqlite

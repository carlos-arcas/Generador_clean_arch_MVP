from pathlib import Path

from blueprints.crud_json_v1.blueprint import CrudJsonBlueprint
from blueprints.crud_sqlite_v1.blueprint import CrudSqliteBlueprint
from dominio.modelos import EspecificacionAtributo, EspecificacionClase


RUTA_SNAPSHOTS = Path("tests/recursos/snapshots")


def _leer_snapshot(nombre_archivo: str) -> str:
    return (RUTA_SNAPSHOTS / nombre_archivo).read_text(encoding="utf-8")


def test_snapshot_crud_json_contenido_multi_atributo() -> None:
    blueprint = CrudJsonBlueprint()
    clase = EspecificacionClase(
        nombre="Cliente",
        atributos=[
            EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True),
            EspecificacionAtributo(nombre="edad", tipo="int", obligatorio=True),
            EspecificacionAtributo(nombre="activo", tipo="bool", obligatorio=True),
        ],
    )

    contenido = blueprint._contenido_test_crud(clase, blueprint._construir_nombres(clase))

    assert contenido == _leer_snapshot("crud_json_test_cliente_multi.py.txt")


def test_snapshot_crud_sqlite_contenido_multi_atributo() -> None:
    blueprint = CrudSqliteBlueprint()
    clase = EspecificacionClase(
        nombre="Cliente",
        atributos=[
            EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True),
            EspecificacionAtributo(nombre="edad", tipo="int", obligatorio=True),
            EspecificacionAtributo(nombre="activo", tipo="bool", obligatorio=True),
        ],
    )

    contenido = blueprint._contenido_repositorio_sqlite(clase, blueprint._construir_nombres(clase))

    assert contenido == _leer_snapshot("crud_sqlite_repositorio_cliente_multi.py.txt")


def test_snapshot_crud_json_contenido_sin_atributos() -> None:
    blueprint = CrudJsonBlueprint()
    clase = EspecificacionClase(nombre="Vacio", atributos=[])

    contenido = blueprint._contenido_test_crud(clase, blueprint._construir_nombres(clase))

    assert contenido == _leer_snapshot("crud_json_test_vacio.py.txt")


def test_snapshot_crud_sqlite_contenido_sin_atributos() -> None:
    blueprint = CrudSqliteBlueprint()
    clase = EspecificacionClase(nombre="Vacio", atributos=[])

    contenido = blueprint._contenido_repositorio_sqlite(clase, blueprint._construir_nombres(clase))

    assert contenido == _leer_snapshot("crud_sqlite_repositorio_vacio.py.txt")

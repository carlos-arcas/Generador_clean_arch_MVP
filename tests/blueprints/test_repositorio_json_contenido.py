from pathlib import Path

from blueprints.crud_json_v1.blueprint import CrudJsonBlueprint
from dominio.modelos import EspecificacionAtributo, EspecificacionClase


RUTA_SNAPSHOTS = Path("tests/recursos/snapshots")


def _leer_snapshot(nombre_archivo: str) -> str:
    return (RUTA_SNAPSHOTS / nombre_archivo).read_text(encoding="utf-8")


def test_contenido_repositorio_json_clase_simple() -> None:
    blueprint = CrudJsonBlueprint()
    clase = EspecificacionClase(
        nombre="Producto",
        atributos=[EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True)],
    )

    contenido = blueprint._contenido_repositorio_json(blueprint._construir_nombres(clase))

    assert contenido == _leer_snapshot("crud_json_repositorio_producto_simple.py.txt")


def test_contenido_repositorio_json_multiples_atributos() -> None:
    blueprint = CrudJsonBlueprint()
    clase = EspecificacionClase(
        nombre="Cliente",
        atributos=[
            EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True),
            EspecificacionAtributo(nombre="edad", tipo="int", obligatorio=True),
            EspecificacionAtributo(nombre="activo", tipo="bool", obligatorio=True),
        ],
    )

    contenido = blueprint._contenido_repositorio_json(blueprint._construir_nombres(clase))

    assert contenido == _leer_snapshot("crud_json_repositorio_cliente_multi.py.txt")


def test_contenido_repositorio_json_sin_atributos() -> None:
    blueprint = CrudJsonBlueprint()
    clase = EspecificacionClase(nombre="Vacio", atributos=[])

    contenido = blueprint._contenido_repositorio_json(blueprint._construir_nombres(clase))

    assert contenido == _leer_snapshot("crud_json_repositorio_vacio_sin_atributos.py.txt")

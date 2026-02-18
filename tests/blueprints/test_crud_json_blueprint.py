import pytest

from blueprints.crud_json_v1.blueprint import CrudJsonBlueprint
from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto, ErrorValidacionDominio


def test_generar_plan_crud_json_con_una_clase() -> None:
    blueprint = CrudJsonBlueprint()
    especificacion = EspecificacionProyecto(
        nombre_proyecto="demo",
        ruta_destino="/tmp/demo",
        clases=[
            EspecificacionClase(
                nombre="Cliente",
                atributos=[
                    EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True),
                    EspecificacionAtributo(nombre="dni", tipo="str", obligatorio=True),
                ],
            )
        ],
    )

    plan = blueprint.generar_plan(especificacion)

    rutas = plan.obtener_rutas()
    esperadas = {
        "datos/.gitkeep",
        "dominio/entidades/cliente.py",
        "aplicacion/puertos/repositorio_cliente.py",
        "aplicacion/casos_uso/cliente/crear_cliente.py",
        "aplicacion/casos_uso/cliente/obtener_cliente.py",
        "aplicacion/casos_uso/cliente/listar_clientes.py",
        "aplicacion/casos_uso/cliente/actualizar_cliente.py",
        "aplicacion/casos_uso/cliente/eliminar_cliente.py",
        "infraestructura/persistencia/json/repositorio_cliente_json.py",
        "tests/aplicacion/test_crud_cliente.py",
        "datos/clientes.json",
    }

    assert esperadas.issubset(set(rutas))
    assert len(rutas) == len(set(rutas))

    contenido_entidad = next(
        item.contenido_texto for item in plan.archivos if item.ruta_relativa == "dominio/entidades/cliente.py"
    )
    contenido_repo = next(
        item.contenido_texto
        for item in plan.archivos
        if item.ruta_relativa == "infraestructura/persistencia/json/repositorio_cliente_json.py"
    )

    assert "@dataclass" in contenido_entidad
    assert "class Cliente" in contenido_entidad
    assert "tempfile.mkstemp" in contenido_repo
    assert "datos" in contenido_repo
    assert "clientes.json" in contenido_repo


def test_generar_plan_crud_json_sin_clases_falla() -> None:
    blueprint = CrudJsonBlueprint()
    especificacion = EspecificacionProyecto(nombre_proyecto="demo", ruta_destino="/tmp/demo")

    with pytest.raises(ErrorValidacionDominio, match="al menos una clase"):
        blueprint.generar_plan(especificacion)

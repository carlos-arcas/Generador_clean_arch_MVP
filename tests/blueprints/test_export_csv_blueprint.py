import pytest

from blueprints.export_csv_v1.blueprint import ExportCsvBlueprint
from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto, ErrorValidacionDominio


def _especificacion_demo() -> EspecificacionProyecto:
    return EspecificacionProyecto(
        nombre_proyecto="demo",
        ruta_destino="/tmp/demo",
        clases=[
            EspecificacionClase(
                nombre="Cliente",
                atributos=[EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True)],
            )
        ],
    )


def test_generar_plan_export_csv_rutas_y_capas() -> None:
    plan = ExportCsvBlueprint().generar_plan(_especificacion_demo())
    rutas = set(plan.obtener_rutas())

    assert "aplicacion/puertos/exportadores/exportador_tabular_csv.py" in rutas
    assert "aplicacion/casos_uso/informes/generar_informe_clientes_csv.py" in rutas
    assert "infraestructura/informes/csv/exportador_csv.py" in rutas
    assert "tests/infraestructura/test_export_csv.py" in rutas
    assert not any(ruta.startswith("dominio/") for ruta in rutas)


def test_export_csv_falla_sin_clases() -> None:
    with pytest.raises(ErrorValidacionDominio, match="al menos una clase"):
        ExportCsvBlueprint().generar_plan(
            EspecificacionProyecto(nombre_proyecto="demo", ruta_destino="/tmp/demo")
        )

import pytest

from blueprints.export_csv_v1.blueprint import ExportCsvBlueprint
from blueprints.export_pdf_v1.blueprint import ExportPdfBlueprint
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


def test_generar_plan_export_pdf_rutas_y_capas() -> None:
    plan = ExportPdfBlueprint().generar_plan(_especificacion_demo())
    rutas = set(plan.obtener_rutas())

    assert "aplicacion/puertos/exportadores/exportador_tabular_pdf.py" in rutas
    assert "aplicacion/casos_uso/informes/generar_informe_clientes_pdf.py" in rutas
    assert "infraestructura/informes/pdf/exportador_pdf_reportlab.py" in rutas
    assert "tests/infraestructura/test_export_pdf.py" in rutas
    assert not any(ruta.startswith("dominio/") for ruta in rutas)


def test_export_pdf_no_conflicta_con_export_csv() -> None:
    plan_pdf = ExportPdfBlueprint().generar_plan(_especificacion_demo())
    plan_csv = ExportCsvBlueprint().generar_plan(_especificacion_demo())

    rutas_pdf = set(plan_pdf.obtener_rutas())
    rutas_csv = set(plan_csv.obtener_rutas())

    assert rutas_pdf.intersection(rutas_csv) == set()


def test_export_pdf_falla_sin_clases() -> None:
    with pytest.raises(ErrorValidacionDominio, match="al menos una clase"):
        ExportPdfBlueprint().generar_plan(
            EspecificacionProyecto(nombre_proyecto="demo", ruta_destino="/tmp/demo")
        )

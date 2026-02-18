from pathlib import Path

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from dominio.modelos import EspecificacionClase, EspecificacionProyecto
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco


def _rutas_plan(blueprints: list[str]) -> list[str]:
    especificacion = EspecificacionProyecto(
        nombre_proyecto="demo",
        ruta_destino="/tmp/demo",
        version="1.0.0",
        clases=[EspecificacionClase(nombre="Cliente")],
    )
    plan = CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco()).ejecutar(
        especificacion,
        blueprints,
    )
    rutas = sorted(plan.obtener_rutas())
    assert len(rutas) == len(set(rutas))
    return rutas


def _leer_snapshot(nombre: str) -> list[str]:
    contenido = Path(f"tests/recursos/snapshots/{nombre}").read_text(encoding="utf-8")
    return [linea.strip() for linea in contenido.splitlines() if linea.strip()]


def test_snapshot_base_crud_json_csv() -> None:
    assert _rutas_plan(["base_clean_arch", "crud_json", "export_csv"]) == _leer_snapshot(
        "base_crud_json_csv.txt"
    )


def test_snapshot_base_sqlite_excel_pdf() -> None:
    assert _rutas_plan(["base_clean_arch", "crud_sqlite", "export_excel", "export_pdf"]) == _leer_snapshot(
        "base_sqlite_excel_pdf.txt"
    )

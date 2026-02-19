"""Snapshot tests v6 para verificar estabilidad de blueprints contra archivos golden."""

from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from dominio.modelos import EspecificacionClase, EspecificacionProyecto
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco

GOLDEN_DIR = Path("tests/snapshots/golden")


def _leer_golden(nombre_archivo: str) -> list[str]:
    return [
        linea.strip()
        for linea in (GOLDEN_DIR / nombre_archivo).read_text(encoding="utf-8").splitlines()
        if linea.strip()
    ]


def _rutas_generadas(blueprints: list[str]) -> list[str]:
    especificacion = EspecificacionProyecto(
        nombre_proyecto="snapshot",
        ruta_destino="/tmp/snapshot",
        version="1.0.0",
        clases=[EspecificacionClase(nombre="Cliente")],
    )
    plan = CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco()).ejecutar(especificacion, blueprints)
    return sorted(plan.obtener_rutas())


def test_snapshot_plan_base_crud_json_csv_contra_golden() -> None:
    assert _rutas_generadas(["base_clean_arch", "crud_json", "export_csv"]) == _leer_golden(
        "base_crud_json_csv.golden.txt"
    )


def test_snapshot_plan_base_sqlite_excel_pdf_contra_golden() -> None:
    assert _rutas_generadas(["base_clean_arch", "crud_sqlite", "export_excel", "export_pdf"]) == _leer_golden(
        "base_sqlite_excel_pdf.golden.txt"
    )

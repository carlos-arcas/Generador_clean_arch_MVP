from __future__ import annotations

from pathlib import Path
import re

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from dominio.modelos import EspecificacionClase, EspecificacionProyecto
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco

GOLDEN_DIR = Path("tests/snapshots/golden")


def _normalizar_linea(linea: str) -> str:
    normalizada = linea.replace("\\", "/")
    normalizada = re.sub(r"/[A-Za-z]:/", "/", normalizada)
    normalizada = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?", "<TIMESTAMP>", normalizada)
    normalizada = re.sub(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F-]{27}\b", "<UUID>", normalizada)
    normalizada = re.sub(r"\btmp/[\w.-]+", "tmp/<TMP>", normalizada)
    return normalizada.strip()


def _leer_golden(nombre: str) -> list[str]:
    return [_normalizar_linea(linea) for linea in (GOLDEN_DIR / nombre).read_text(encoding="utf-8").splitlines() if linea.strip()]


def _plan_normalizado(blueprints: list[str]) -> list[str]:
    especificacion = EspecificacionProyecto(
        nombre_proyecto="snapshot",
        ruta_destino="/tmp/snapshot",
        version="1.0.0",
        clases=[EspecificacionClase(nombre="Cliente")],
    )
    plan = CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco()).ejecutar(especificacion, blueprints)
    return sorted(_normalizar_linea(ruta) for ruta in plan.obtener_rutas())


def test_snapshot_base_crud_json_csv() -> None:
    assert _plan_normalizado(["base_clean_arch", "crud_json", "export_csv"]) == _leer_golden("base_crud_json_csv.golden.txt")


def test_snapshot_base_sqlite_excel_pdf() -> None:
    assert _plan_normalizado(["base_clean_arch", "crud_sqlite", "export_excel", "export_pdf"]) == _leer_golden(
        "base_sqlite_excel_pdf.golden.txt"
    )

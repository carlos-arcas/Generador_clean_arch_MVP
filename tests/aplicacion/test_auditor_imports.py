from pathlib import Path

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos, ResultadoProceso


class EjecutorFalso(EjecutorProcesos):
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return ResultadoProceso(0, "TOTAL 10 1 90%", "")


def _crear_base(base: Path) -> None:
    for carpeta in ["dominio", "aplicacion", "infraestructura", "presentacion", "tests", "scripts", "logs", "docs"]:
        (base / carpeta).mkdir(parents=True)
    (base / "VERSION").write_text("0.7.0", encoding="utf-8")
    (base / "CHANGELOG.md").write_text("# CHANGELOG", encoding="utf-8")
    (base / "infraestructura" / "logging_config.py").write_text("def configurar_logging(): pass", encoding="utf-8")
    (base / "logs" / "seguimiento.log").write_text("", encoding="utf-8")
    (base / "logs" / "crashes.log").write_text("", encoding="utf-8")


def test_auditor_imports_prohibidos_en_dominio(tmp_path: Path) -> None:
    _crear_base(tmp_path)
    (tmp_path / "dominio" / "modelo.py").write_text("import json\nfrom infraestructura.servicio import X\n", encoding="utf-8")

    resultado = AuditarProyectoGenerado(EjecutorFalso()).ejecutar(str(tmp_path))

    assert resultado.valido is False
    assert any("Import prohibido en dominio" in error for error in resultado.lista_errores)


def test_auditor_detecta_import_circular_basico(tmp_path: Path) -> None:
    _crear_base(tmp_path)
    (tmp_path / "aplicacion" / "a.py").write_text("from aplicacion.b import B\n", encoding="utf-8")
    (tmp_path / "aplicacion" / "b.py").write_text("from aplicacion.a import A\n", encoding="utf-8")

    resultado = AuditarProyectoGenerado(EjecutorFalso()).ejecutar(str(tmp_path))

    assert resultado.valido is False
    assert any("Import circular detectado" in error for error in resultado.lista_errores)


def test_auditor_rechaza_sqlite3_fuera_de_infraestructura(tmp_path: Path) -> None:
    _crear_base(tmp_path)
    (tmp_path / "aplicacion" / "caso.py").write_text("import sqlite3\n", encoding="utf-8")

    resultado = AuditarProyectoGenerado(EjecutorFalso()).ejecutar(str(tmp_path))

    assert resultado.valido is False
    assert any("sqlite3 fuera de infraestructura" in error for error in resultado.lista_errores)


def test_auditor_permite_sqlite3_en_infraestructura(tmp_path: Path) -> None:
    _crear_base(tmp_path)
    (tmp_path / "infraestructura" / "repo.py").write_text("import sqlite3\n", encoding="utf-8")

    resultado = AuditarProyectoGenerado(EjecutorFalso()).ejecutar(str(tmp_path))

    assert resultado.valido is True


def test_auditor_rechaza_openpyxl_fuera_de_infraestructura(tmp_path: Path) -> None:
    _crear_base(tmp_path)
    (tmp_path / "aplicacion" / "caso.py").write_text("from openpyxl import Workbook\n", encoding="utf-8")

    resultado = AuditarProyectoGenerado(EjecutorFalso()).ejecutar(str(tmp_path))

    assert resultado.valido is False
    assert any("openpyxl fuera de infraestructura" in error for error in resultado.lista_errores)


def test_auditor_requiere_dependencias_si_hay_blueprints_informes(tmp_path: Path) -> None:
    _crear_base(tmp_path)
    (tmp_path / "requirements.txt").write_text("pytest==8.3.3\n", encoding="utf-8")

    resultado = AuditarProyectoGenerado(EjecutorFalso()).ejecutar(
        str(tmp_path),
        blueprints_usados=["base_clean_arch", "crud_json", "export_excel", "export_pdf"],
    )

    assert resultado.valido is False
    assert any("openpyxl" in error for error in resultado.lista_errores)
    assert any("reportlab" in error for error in resultado.lista_errores)

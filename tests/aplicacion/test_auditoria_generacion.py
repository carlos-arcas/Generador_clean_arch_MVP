from __future__ import annotations

import json
from pathlib import Path

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado


def _crear_proyecto_valido(base: Path) -> None:
    for carpeta in (
        "dominio",
        "aplicacion",
        "infraestructura",
        "presentacion",
        "tests",
        "docs",
        "logs",
        "configuracion",
        "scripts",
    ):
        (base / carpeta).mkdir(parents=True, exist_ok=True)

    (base / "VERSION").write_text("1.0.0", encoding="utf-8")
    (base / "CHANGELOG.md").write_text("# Changelog", encoding="utf-8")
    (base / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    (base / "dominio" / "entidad.py").write_text("class Entidad: ...\n", encoding="utf-8")
    (base / "aplicacion" / "caso_uso.py").write_text("from dominio.entidad import Entidad\n", encoding="utf-8")
    (base / "configuracion" / "MANIFEST.json").write_text(
        json.dumps({"version_generador": "1.0.0", "archivos_generados": 2}),
        encoding="utf-8",
    )


def test_proyecto_valido_retorna_valido_true(tmp_path: Path) -> None:
    _crear_proyecto_valido(tmp_path)

    resultado = AuditarProyectoGenerado().auditar(str(tmp_path))

    assert resultado.valido is True
    assert resultado.errores == []


def test_falta_carpeta_dominio_detecta_error(tmp_path: Path) -> None:
    _crear_proyecto_valido(tmp_path)
    (tmp_path / "dominio" / "entidad.py").unlink()
    (tmp_path / "dominio").rmdir()

    resultado = AuditarProyectoGenerado().auditar(str(tmp_path))

    assert resultado.valido is False
    assert any("dominio" in error for error in resultado.errores)


def test_import_ilegal_en_dominio_detecta_error(tmp_path: Path) -> None:
    _crear_proyecto_valido(tmp_path)
    (tmp_path / "dominio" / "entidad.py").write_text(
        "from infraestructura.repo import Repo\n",
        encoding="utf-8",
    )

    resultado = AuditarProyectoGenerado().auditar(str(tmp_path))

    assert resultado.valido is False
    assert any("Import prohibido en dominio" in error for error in resultado.errores)

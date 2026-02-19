from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado


_DIRECTORIOS_BASE = [
    "dominio",
    "aplicacion",
    "infraestructura",
    "presentacion",
    "tests",
    "docs",
    "logs",
    "configuracion",
    "scripts",
]


def _crear_estructura_minima(base: Path) -> None:
    for carpeta in _DIRECTORIOS_BASE:
        (base / carpeta).mkdir(parents=True, exist_ok=True)
    (base / "VERSION").write_text("1.0.0", encoding="utf-8")
    (base / "CHANGELOG.md").write_text("inicio", encoding="utf-8")
    (base / "requirements.txt").write_text("", encoding="utf-8")
    (base / "configuracion" / "MANIFEST.json").write_text("{}", encoding="utf-8")


def test_auditoria_detecta_violacion_real_de_capa(tmp_path: Path) -> None:
    proyecto = tmp_path / "proyecto_auditado"
    _crear_estructura_minima(proyecto)
    (proyecto / "dominio" / "modelo.py").write_text("from infraestructura.repo import Repo\n", encoding="utf-8")

    resultado = AuditarProyectoGenerado().auditar(str(proyecto))

    assert resultado.valido is False
    assert any("dominio" in error.lower() and "infraestructura" in error.lower() for error in resultado.errores)

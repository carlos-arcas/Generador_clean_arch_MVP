from __future__ import annotations

import inspect
import json
from pathlib import Path

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_aplicacion_no_depende_infraestructura import (
    ReglaAplicacionNoDependeInfraestructura,
)
from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_dominio_no_depende_de_otras_capas import (
    ReglaDominioNoDependeDeOtrasCapas,
)
from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_presentacion_no_depende_dominio import (
    ReglaPresentacionNoDependeDominio,
)
from aplicacion.casos_uso.auditoria.validadores.validador_base import ContextoAuditoria


def _crear_proyecto_base(tmp_path: Path) -> None:
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
        (tmp_path / carpeta).mkdir(parents=True, exist_ok=True)

    (tmp_path / "VERSION").write_text("1.0.0", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    (tmp_path / "configuracion" / "MANIFEST.json").write_text(
        json.dumps({"version_generador": "1.0.0", "archivos_generados": 2}),
        encoding="utf-8",
    )


def test_regla_presentacion_no_depende_dominio_detecta_import_indebido(tmp_path: Path) -> None:
    _crear_proyecto_base(tmp_path)
    (tmp_path / "aplicacion" / "caso_uso.py").write_text("from presentacion.ui import Vista\n", encoding="utf-8")

    resultado = ReglaPresentacionNoDependeDominio().evaluar(ContextoAuditoria(base=tmp_path))

    assert resultado.exito is False
    assert any("Import prohibido en aplicacion" in error for error in resultado.errores)


def test_regla_aplicacion_no_depende_infraestructura_detecta_violacion(tmp_path: Path) -> None:
    _crear_proyecto_base(tmp_path)
    (tmp_path / "dominio" / "entidad.py").write_text("from infraestructura.repo import Repo\n", encoding="utf-8")

    resultado = ReglaAplicacionNoDependeInfraestructura().evaluar(ContextoAuditoria(base=tmp_path))

    assert resultado.exito is False
    assert any("Import prohibido en dominio" in error for error in resultado.errores)


def test_regla_dominio_no_depende_de_otras_capas_detecta_violacion(tmp_path: Path) -> None:
    _crear_proyecto_base(tmp_path)
    (tmp_path / "dominio" / "entidad.py").write_text("from presentacion.ui import Vista\n", encoding="utf-8")

    resultado = ReglaDominioNoDependeDeOtrasCapas().evaluar(ContextoAuditoria(base=tmp_path))

    assert resultado.exito is False
    assert any("Import prohibido en dominio" in error for error in resultado.errores)


def test_reglas_dependencias_sin_violaciones(tmp_path: Path) -> None:
    _crear_proyecto_base(tmp_path)
    (tmp_path / "dominio" / "entidad.py").write_text("class Entidad: ...\n", encoding="utf-8")
    (tmp_path / "aplicacion" / "caso_uso.py").write_text("from dominio.entidad import Entidad\n", encoding="utf-8")

    resultado = AuditarProyectoGenerado().auditar(str(tmp_path))

    assert resultado.valido is True
    assert resultado.errores == []


def test_validar_dependencias_capas_es_orquestador_reducido() -> None:
    codigo = inspect.getsource(AuditarProyectoGenerado._validar_dependencias_capas)

    assert len(codigo.splitlines()) < 40

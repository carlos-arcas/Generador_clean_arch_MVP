from pathlib import Path

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado


def _crear_estructura_minima(base: Path) -> None:
    (base / "logs").mkdir(parents=True)
    (base / "scripts").mkdir(parents=True)
    (base / "manifest.json").write_text("{}", encoding="utf-8")
    (base / "README.md").write_text("# Demo", encoding="utf-8")
    (base / "VERSION").write_text("0.2.0", encoding="utf-8")
    (base / "scripts" / "lanzar_app.bat").write_text("echo run", encoding="utf-8")
    (base / "scripts" / "ejecutar_tests.bat").write_text("echo test", encoding="utf-8")


def test_auditar_proyecto_valido(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)

    resultado = AuditarProyectoGenerado().ejecutar(str(tmp_path))

    assert resultado.valido is True
    assert resultado.lista_errores == []


def test_auditar_proyecto_con_faltantes(tmp_path: Path) -> None:
    resultado = AuditarProyectoGenerado().ejecutar(str(tmp_path))

    assert resultado.valido is False
    assert len(resultado.lista_errores) == 6

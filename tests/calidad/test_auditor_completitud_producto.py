from __future__ import annotations

from pathlib import Path

from herramientas.auditar_completitud_producto import auditar_completitud_producto, main


def _crear_archivo(ruta: Path, contenido: str = "") -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf-8")


def _crear_repo_minimo(base: Path) -> None:
    for carpeta in [
        "dominio",
        "aplicacion",
        "infraestructura",
        "presentacion",
        "tests/dominio",
        "tests/aplicacion",
        "tests/infraestructura",
        "tests/presentacion",
        "tests/integracion",
        "tests/snapshots/golden",
        "docs",
        "logs",
        "configuracion",
        "scripts",
    ]:
        (base / carpeta).mkdir(parents=True, exist_ok=True)

    _crear_archivo(base / "dominio" / "entidad.py", "def funcion_publica() -> int:\n    return 1\n")
    _crear_archivo(base / "aplicacion" / "servicio.py", "class Servicio:\n    pass\n")
    _crear_archivo(base / "infraestructura" / "logging_config.py", "from logging.handlers import RotatingFileHandler\nimport sys\nFORMATO='%(asctime)s %(levelname)s %(message)s'\nsys.excepthook = lambda *args: None\n")
    _crear_archivo(base / "presentacion" / "mapeo_mensajes_error.py", "def mapear_error_a_mensaje_ux(*_args):\n    return None\n")
    _crear_archivo(
        base / "presentacion" / "dialogo_error.py",
        "from PySide6.QtWidgets import QMessageBox\n"
        "from presentacion.mapeo_mensajes_error import mapear_error_a_mensaje_ux\n"
        "def mostrar(exc):\n"
        "    mapear_error_a_mensaje_ux(exc, 'ID', None)\n"
        "    QMessageBox.critical(None, 'Error', 'ID de incidente: ID')\n",
    )

    _crear_archivo(base / "tests" / "dominio" / "test_entidad.py", "from dominio.entidad import funcion_publica\n\ndef test_ok():\n    assert funcion_publica() == 1\n")
    _crear_archivo(base / "tests" / "aplicacion" / "test_servicio.py", "from aplicacion.servicio import Servicio\n\ndef test_servicio():\n    assert Servicio is not None\n")
    _crear_archivo(base / "tests" / "infraestructura" / "test_dummy.py", "def test_dummy():\n    assert True\n")
    _crear_archivo(base / "tests" / "presentacion" / "test_dummy.py", "def test_dummy():\n    assert True\n")

    _crear_archivo(base / "pytest.ini", "[pytest]\n")
    _crear_archivo(base / "scripts" / "lanzar_app.bat", "if not exist .venv python -m venv .venv\ncall .venv\\Scripts\\activate\npip install -r requirements.txt\npython -m presentacion\n")
    _crear_archivo(base / "scripts" / "ejecutar_tests.bat", "if not exist .venv python -m venv .venv\ncall .venv\\Scripts\\activate\npip install -r requirements.txt\npytest -q --maxfail=1\npytest --cov=. --cov-report=term-missing --cov-fail-under=85\necho TODO OK\necho FALLOS EN TESTS\nif errorlevel 1 exit /b 1\n")

    for doc in [
        "README.md",
        "arquitectura.md",
        "decisiones_tecnicas.md",
        "guia_pruebas.md",
        "guia_logging.md",
        "auditoria_completitud_producto.md",
    ]:
        contenido = "Diagrama -> capa\n" if doc == "arquitectura.md" else "contenido cov\n"
        _crear_archivo(base / "docs" / doc, contenido)

    _crear_archivo(base / "logs" / "seguimiento.log", "")
    _crear_archivo(base / "logs" / "crashes.log", "")
    _crear_archivo(base / "VERSION", "1.2.3\n")
    _crear_archivo(base / "CHANGELOG.md", "## 1.2.3\n")


def test_auditoria_repo_minimo_ok(tmp_path: Path, monkeypatch) -> None:
    _crear_repo_minimo(tmp_path)
    resultado = auditar_completitud_producto(tmp_path)
    assert resultado.puntaje_total > 45
    assert resultado.codigo_salida == 0

    monkeypatch.chdir(tmp_path)
    assert main() == 0


def test_auditoria_falla_critica_si_falta_script_tests(tmp_path: Path) -> None:
    _crear_repo_minimo(tmp_path)
    (tmp_path / "scripts" / "ejecutar_tests.bat").unlink()

    resultado = auditar_completitud_producto(tmp_path)

    assert resultado.codigo_salida != 0
    assert any("ejecutar_tests.bat" in hallazgo.descripcion for hallazgo in resultado.hallazgos)


def test_auditoria_detecta_print(tmp_path: Path) -> None:
    _crear_repo_minimo(tmp_path)
    _crear_archivo(tmp_path / "dominio" / "consola.py", "def demo():\n    print('debug')\n")

    resultado = auditar_completitud_producto(tmp_path)

    assert any("print(" in item for item in resultado.prints_detectados)

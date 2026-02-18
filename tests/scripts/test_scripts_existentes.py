from pathlib import Path


def test_scripts_bat_existen() -> None:
    raiz = Path(__file__).resolve().parents[2]
    for nombre in ("lanzar_app.bat", "lanzar_cli.bat", "ejecutar_tests.bat"):
        assert (raiz / "scripts" / nombre).exists(), f"No existe scripts/{nombre}"


def test_contenido_minimo_scripts() -> None:
    raiz = Path(__file__).resolve().parents[2]

    contenido_app = (raiz / "scripts" / "lanzar_app.bat").read_text(encoding="utf-8")
    contenido_cli = (raiz / "scripts" / "lanzar_cli.bat").read_text(encoding="utf-8")
    contenido_tests = (raiz / "scripts" / "ejecutar_tests.bat").read_text(encoding="utf-8")

    assert 'cd /d "%~dp0\\.."' in contenido_app
    assert 'cd /d "%~dp0\\.."' in contenido_cli
    assert 'cd /d "%~dp0\\.."' in contenido_tests

    assert "pytest -q --maxfail=1" in contenido_tests
    assert "--cov-fail-under=85" in contenido_tests

    assert "exit /b 0" in contenido_app
    assert "exit /b 0" in contenido_cli
    assert "exit /b 0" in contenido_tests
    assert "exit /b 1" in contenido_tests

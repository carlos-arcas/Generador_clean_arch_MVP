"""Pruebas de robustez de la fábrica de credenciales."""

from __future__ import annotations

import pytest

from aplicacion.errores import ErrorInfraestructura
from infraestructura.seguridad.fabrica_repositorio_credenciales import SelectorRepositorioCredenciales
from infraestructura.seguridad.repositorio_credenciales_memoria import RepositorioCredencialesMemoria


def test_crear_repositorio_windows_preserva_causa(monkeypatch: pytest.MonkeyPatch) -> None:
    import infraestructura.seguridad.fabrica_repositorio_credenciales as modulo

    monkeypatch.setattr(modulo.sys, "platform", "win32")

    def _fallar_windows() -> object:
        raise OSError("No hay acceso a Credential Manager")

    monkeypatch.setattr(modulo, "RepositorioCredencialesWindows", _fallar_windows)
    selector = SelectorRepositorioCredenciales()

    with pytest.raises(ErrorInfraestructura) as exc_info:
        selector._crear_repositorio_windows()

    assert isinstance(exc_info.value.__cause__, OSError)
    assert "No hay acceso" in str(exc_info.value.__cause__)


def test_crear_hace_fallback_a_memoria_si_falla_windows(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    import infraestructura.seguridad.fabrica_repositorio_credenciales as modulo

    monkeypatch.setattr(modulo.sys, "platform", "win32")

    def _fallar_windows() -> object:
        raise PermissionError("Acceso denegado")

    monkeypatch.setattr(modulo, "RepositorioCredencialesWindows", _fallar_windows)

    selector = SelectorRepositorioCredenciales()
    with caplog.at_level("WARNING"):
        repositorio = selector.crear()

    assert isinstance(repositorio, RepositorioCredencialesMemoria)
    assert "se usará memoria temporal" in caplog.text

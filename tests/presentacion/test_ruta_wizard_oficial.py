"""Pruebas de wiring para la ruta oficial del wizard."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from presentacion import __main__ as modulo_main
from presentacion.wizard.wizard_generador import WizardGeneradorProyectos


class _FakeApp:
    def __init__(self, argv: list[str]) -> None:
        self.argv = argv

    def exec(self) -> int:
        return 0


class _FakeContenedor:
    def __init__(self) -> None:
        self.generar_proyecto_mvp = object()
        self.guardar_preset_proyecto = object()
        self.cargar_preset_proyecto = object()
        self.guardar_credencial = object()
        self.catalogo_blueprints = [("base_clean_arch", "1.0.0", "base")]


class _SpyWizard:
    creado_con: dict[str, object] | None = None
    mostrado = False

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        type(self).creado_con = kwargs

    def show(self) -> None:
        type(self).mostrado = True


def test_entrypoint_usa_wizard_oficial(monkeypatch: pytest.MonkeyPatch) -> None:
    assert modulo_main.WizardGeneradorProyectos is WizardGeneradorProyectos

    monkeypatch.setattr(modulo_main, "QApplication", _FakeApp)
    monkeypatch.setattr(modulo_main, "crear_contenedor", lambda: _FakeContenedor())
    monkeypatch.setattr(modulo_main, "WizardGeneradorProyectos", _SpyWizard)

    codigo = modulo_main.main()

    assert codigo == 0
    assert _SpyWizard.mostrado is True
    assert _SpyWizard.creado_con is not None
    assert "generar_proyecto" in _SpyWizard.creado_con

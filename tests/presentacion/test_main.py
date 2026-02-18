"""Pruebas del punto de entrada de presentación."""

from __future__ import annotations

import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from presentacion import __main__ as modulo_main


class _FakeApp:
    def __init__(self, argv: list[str]) -> None:
        self.argv = argv

    def exec(self) -> int:
        return 0


class _FakeWizard:
    def __init__(self) -> None:
        self.mostrado = False

    def show(self) -> None:
        self.mostrado = True


def test_main_inicializa_app_qt(monkeypatch) -> None:
    monkeypatch.setattr(modulo_main, "QApplication", _FakeApp)
    monkeypatch.setattr(modulo_main, "WizardGeneradorProyectos", _FakeWizard)

    codigo = modulo_main.main()

    assert codigo == 0

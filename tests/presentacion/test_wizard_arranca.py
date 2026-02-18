"""Pruebas de arranque del wizard principal."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication

from presentacion.wizard.wizard_generador import WizardGeneradorProyectos


@pytest.fixture
def app_qt() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def test_wizard_generador_arranca_sin_crashear(app_qt: QApplication) -> None:
    wizard = WizardGeneradorProyectos()

    assert wizard is not None
    assert len(wizard.pageIds()) == 4

"""Pruebas de robustez de PaginaClases sin asociación temprana a QWizard."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication

from presentacion.wizard.paginas.pagina_clases import PaginaClases


@pytest.fixture
def app_qt() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def test_instanciar_pagina_clases_sin_wizard_no_crashea(app_qt: QApplication) -> None:
    pagina = PaginaClases()

    assert pagina.isComplete() is False
    assert pagina.panel_atributos_habilitado() is False

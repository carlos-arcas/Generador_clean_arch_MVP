"""Pruebas mínimas de wiring para capa de presentación PySide6."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication

from presentacion.ventana_principal import VentanaPrincipal
from presentacion.wizard.paginas.pagina_persistencia import PaginaPersistencia


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def test_instanciar_ventana_principal() -> None:
    _app()
    ventana = VentanaPrincipal(version_generador="0.7.0")

    assert ventana.windowTitle() == "Generador Base Proyectos"
    assert ventana.wizard is not None


def test_pagina_persistencia_expone_blueprints_seleccionados() -> None:
    _app()
    pagina = PaginaPersistencia()
    pagina.establecer_blueprints_disponibles(
        [
            ("base_clean_arch", "1.0.0", "Base"),
            ("crud_json", "1.0.0", "CRUD JSON"),
        ],
        seleccionados=["base_clean_arch"],
    )

    assert pagina.blueprints_seleccionados() == ["base_clean_arch"]

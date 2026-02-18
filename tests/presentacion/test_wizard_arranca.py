"""Pruebas de arranque del wizard principal."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication

from infraestructura.bootstrap import construir_contenedor_aplicacion
from presentacion.wizard.wizard_generador import WizardGeneradorProyectos


def crear_wizard(**sobrescrituras):
    contenedor = construir_contenedor_aplicacion()
    dependencias = {
        "generar_proyecto": contenedor.generar_proyecto_mvp,
        "guardar_preset": contenedor.guardar_preset_proyecto,
        "cargar_preset": contenedor.cargar_preset_proyecto,
        "guardar_credencial": contenedor.guardar_credencial,
        "catalogo_blueprints": contenedor.catalogo_blueprints,
    }
    dependencias.update(sobrescrituras)
    return WizardGeneradorProyectos(**dependencias)


@pytest.fixture
def app_qt() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def test_wizard_generador_arranca_sin_crashear(app_qt: QApplication) -> None:
    wizard = crear_wizard()

    assert wizard is not None
    assert len(wizard.pageIds()) == 4

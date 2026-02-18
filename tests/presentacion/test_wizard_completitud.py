"""Pruebas de completitud de páginas del wizard."""

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


def test_pagina_datos_is_complete_depende_de_nombre_y_ruta(app_qt: QApplication) -> None:
    wizard = crear_wizard()
    pagina = wizard.pagina_datos

    pagina.campo_nombre.setText("   ")
    pagina.campo_ruta.setText("")
    assert pagina.isComplete() is False

    pagina.campo_nombre.setText("Proyecto Demo")
    pagina.campo_ruta.setText("/tmp/destino")
    assert pagina.isComplete() is True


def test_pagina_clases_is_complete_depende_de_existencia_de_clases(app_qt: QApplication) -> None:
    wizard = crear_wizard()
    pagina = wizard.pagina_clases

    assert pagina.isComplete() is False

    assert pagina.anadir_clase("Cliente") is True
    assert pagina.isComplete() is True

    assert pagina.eliminar_clase_seleccionada() is True
    assert pagina.isComplete() is False

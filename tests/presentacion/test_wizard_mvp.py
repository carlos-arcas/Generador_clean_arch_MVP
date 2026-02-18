"""Pruebas del wizard MVP de 4 pasos."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication

from aplicacion.dtos.proyecto import DtoAtributo, DtoClase
from presentacion.wizard.paginas.pagina_resumen import PaginaResumen
from presentacion.wizard.wizard_generador import WizardGeneradorProyectos


@pytest.fixture
def app_qt() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def test_wizard_instancia_sin_errores(app_qt: QApplication) -> None:
    wizard = WizardGeneradorProyectos()

    assert wizard.pageIds() == [0, 1, 2, 3]


def test_pagina_datos_complete_valida_nombre_y_ruta(app_qt: QApplication) -> None:
    wizard = WizardGeneradorProyectos()
    pagina = wizard.pagina_datos

    pagina.campo_nombre.setText("")
    pagina.campo_ruta.setText("")
    assert pagina.isComplete() is False

    pagina.campo_nombre.setText("MiProyecto")
    pagina.campo_ruta.setText("/tmp/salida")
    assert pagina.isComplete() is True


def test_anadir_clase_evitar_duplicados(app_qt: QApplication) -> None:
    wizard = WizardGeneradorProyectos()
    pagina = wizard.pagina_clases

    assert pagina.anadir_clase("Usuario") is True
    assert pagina.anadir_clase("Usuario") is False
    assert pagina.clases() == ["Usuario"]


def test_persistencia_por_defecto_json(app_qt: QApplication) -> None:
    wizard = WizardGeneradorProyectos()

    assert wizard.pagina_persistencia.persistencia_seleccionada() == "JSON"


def test_pagina_resumen_contiene_nombre_y_persistencia(app_qt: QApplication) -> None:
    pagina = PaginaResumen()

    clases = [DtoClase(nombre="Producto", atributos=[DtoAtributo(nombre="id", tipo="int", obligatorio=True)])]

    resumen = pagina.construir_resumen(
        nombre="Inventario",
        ruta="/tmp/inventario",
        descripcion="Sistema de inventario",
        version="1.0.1",
        clases=clases,
        persistencia="SQLite",
    )

    assert "Inventario" in resumen
    assert "Persistencia: SQLite" in resumen
    assert "Clase: Producto" in resumen
    assert "id: int (obligatorio)" in resumen

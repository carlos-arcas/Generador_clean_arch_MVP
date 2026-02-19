"""Pruebas de inicialización y wiring básico de PaginaClases."""

from __future__ import annotations

import inspect
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


def test_instancia_pagina_clases_sin_error(app_qt: QApplication) -> None:
    pagina = PaginaClases()

    assert pagina is not None


def test_componentes_clave_existen(app_qt: QApplication) -> None:
    pagina = PaginaClases()

    assert pagina._campo_nombre_clase is not None
    assert pagina._lista_clases is not None
    assert pagina._boton_anadir_clase is not None
    assert pagina._boton_eliminar_clase is not None
    assert pagina._tabla_atributos is not None
    assert pagina._campo_nombre_atributo is not None
    assert pagina._combo_tipo_atributo is not None
    assert pagina._checkbox_obligatorio is not None
    assert pagina._boton_anadir_atributo is not None
    assert pagina._boton_eliminar_atributo is not None
    assert pagina._clases_dto is not None


def test_init_tiene_menos_de_setenta_lineas() -> None:
    codigo_init = inspect.getsource(PaginaClases.__init__)

    assert len(codigo_init.strip().splitlines()) < 70

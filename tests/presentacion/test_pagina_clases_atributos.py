"""Pruebas unitarias de gestión de clases y atributos en la página de clases."""

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


def test_anadir_clase_valida(app_qt: QApplication) -> None:
    pagina = PaginaClases()

    assert pagina.anadir_clase("Cliente") is True
    assert pagina.clases() == ["Cliente"]


def test_no_permitir_clase_duplicada(app_qt: QApplication) -> None:
    pagina = PaginaClases()

    assert pagina.anadir_clase("Cliente") is True
    assert pagina.anadir_clase("Cliente") is False
    assert pagina.clases() == ["Cliente"]


def test_anadir_atributo_valido(app_qt: QApplication) -> None:
    pagina = PaginaClases()
    pagina.anadir_clase("Cliente")

    assert pagina.anadir_atributo(nombre_atributo="nombre", tipo="str", obligatorio=True) is True
    clases = pagina.clases_temporales()
    assert len(clases[0].atributos) == 1
    assert clases[0].atributos[0].nombre == "nombre"


def test_no_permitir_atributo_duplicado(app_qt: QApplication) -> None:
    pagina = PaginaClases()
    pagina.anadir_clase("Cliente")

    assert pagina.anadir_atributo(nombre_atributo="nombre", tipo="str", obligatorio=False) is True
    assert pagina.anadir_atributo(nombre_atributo="nombre", tipo="str", obligatorio=True) is False


def test_eliminar_atributo(app_qt: QApplication) -> None:
    pagina = PaginaClases()
    pagina.anadir_clase("Cliente")
    pagina.anadir_atributo(nombre_atributo="nombre", tipo="str", obligatorio=False)
    assert pagina.seleccionar_atributo(0) is True

    assert pagina.eliminar_atributo_seleccionado() is True
    assert pagina.clases_temporales()[0].atributos == []


def test_eliminar_clase_elimina_sus_atributos(app_qt: QApplication) -> None:
    pagina = PaginaClases()
    pagina.anadir_clase("Cliente")
    pagina.anadir_atributo(nombre_atributo="nombre", tipo="str", obligatorio=False)

    assert pagina.eliminar_clase_seleccionada() is True
    assert pagina.clases_temporales() == []


def test_panel_atributos_deshabilitado_sin_clase_seleccionada(app_qt: QApplication) -> None:
    pagina = PaginaClases()

    assert pagina.panel_atributos_habilitado() is False

    pagina.anadir_clase("Cliente")
    assert pagina.panel_atributos_habilitado() is True

    pagina.limpiar_seleccion_clase()
    assert pagina.panel_atributos_habilitado() is False

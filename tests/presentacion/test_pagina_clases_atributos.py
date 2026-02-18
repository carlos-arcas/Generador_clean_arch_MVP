"""Pruebas unitarias de gestión de clases y atributos en la página de clases."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication
QMessageBox = QtWidgets.QMessageBox

from presentacion.wizard.wizard_generador import WizardGeneradorProyectos


@pytest.fixture
def app_qt() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


@pytest.fixture
def wizard(app_qt: QApplication, monkeypatch: pytest.MonkeyPatch) -> WizardGeneradorProyectos:
    monkeypatch.setattr(QMessageBox, "critical", lambda *args, **kwargs: QMessageBox.Ok)
    return WizardGeneradorProyectos()


def test_anadir_clase_valida(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases

    assert pagina.anadir_clase("Cliente") is True
    assert pagina.clases() == ["Cliente"]


def test_no_permitir_clase_duplicada(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases

    assert pagina.anadir_clase("Cliente") is True
    assert pagina.anadir_clase("Cliente") is False
    assert pagina.clases() == ["Cliente"]


def test_anadir_atributo_valido(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases
    pagina.anadir_clase("Cliente")

    assert pagina.anadir_atributo(nombre_atributo="nombre", tipo="str", obligatorio=True) is True
    clases = pagina.dto_clases()
    assert len(clases[0].atributos) == 1
    assert clases[0].atributos[0].nombre == "nombre"


def test_no_permitir_atributo_duplicado(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases
    pagina.anadir_clase("Cliente")

    assert pagina.anadir_atributo(nombre_atributo="nombre", tipo="str", obligatorio=False) is True
    assert pagina.anadir_atributo(nombre_atributo="nombre", tipo="str", obligatorio=True) is False


def test_eliminar_atributo(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases
    pagina.anadir_clase("Cliente")
    pagina.anadir_atributo(nombre_atributo="nombre", tipo="str", obligatorio=False)
    assert pagina.seleccionar_atributo(0) is True

    assert pagina.eliminar_atributo_seleccionado() is True
    assert pagina.dto_clases()[0].atributos == []


def test_eliminar_clase_elimina_sus_atributos(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases
    pagina.anadir_clase("Cliente")
    pagina.anadir_atributo(nombre_atributo="nombre", tipo="str", obligatorio=False)

    assert pagina.eliminar_clase_seleccionada() is True
    assert pagina.dto_clases() == []


def test_panel_atributos_deshabilitado_sin_clase_seleccionada(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases

    assert pagina.panel_atributos_habilitado() is False

    pagina.anadir_clase("Cliente")
    assert pagina.panel_atributos_habilitado() is True

    pagina.limpiar_seleccion_clase()
    assert pagina.panel_atributos_habilitado() is False

"""Pruebas de integración entre wizard y modelo de dominio real."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication
QMessageBox = QtWidgets.QMessageBox

from dominio.modelos import ErrorValidacionDominio, EspecificacionAtributo, EspecificacionClase
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


def test_anadir_clase_valida_aparece_en_especificacion(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases

    assert pagina.anadir_clase("Cliente") is True
    assert [clase.nombre for clase in wizard.especificacion_proyecto.clases] == ["Cliente"]


def test_clase_duplicada_lanza_excepcion_en_dominio(wizard: WizardGeneradorProyectos) -> None:
    wizard.especificacion_proyecto.agregar_clase(EspecificacionClase(nombre="Cliente"))

    with pytest.raises(ErrorValidacionDominio):
        wizard.especificacion_proyecto.agregar_clase(EspecificacionClase(nombre="Cliente"))


def test_anadir_atributo_valido(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases
    pagina.anadir_clase("Cliente")

    assert pagina.anadir_atributo(nombre_atributo="edad", tipo="int", obligatorio=False) is True
    atributo = wizard.especificacion_proyecto.clases[0].atributos[0]
    assert atributo.nombre == "edad"
    assert atributo.tipo == "int"


def test_atributo_duplicado_lanza_excepcion_en_dominio(wizard: WizardGeneradorProyectos) -> None:
    clase = EspecificacionClase(nombre="Cliente")
    clase.agregar_atributo(EspecificacionAtributo(nombre="email", tipo="str", obligatorio=True))

    with pytest.raises(ErrorValidacionDominio):
        clase.agregar_atributo(EspecificacionAtributo(nombre="email", tipo="str", obligatorio=False))


def test_especificacion_final_contiene_estructura_esperada(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases
    pagina.anadir_clase("Cliente")
    pagina.anadir_atributo(nombre_atributo="nombre", tipo="str", obligatorio=True)
    pagina.anadir_clase("Pedido")
    pagina.anadir_atributo(nombre_atributo="total", tipo="float", obligatorio=True)

    estructura = {
        clase.nombre: [(atributo.nombre, atributo.tipo, atributo.obligatorio) for atributo in clase.atributos]
        for clase in wizard.especificacion_proyecto.clases
    }

    assert estructura == {
        "Cliente": [("nombre", "str", True)],
        "Pedido": [("total", "float", True)],
    }

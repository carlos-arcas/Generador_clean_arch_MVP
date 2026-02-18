"""Pruebas de integración entre wizard y DTOs de aplicación."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication
QMessageBox = QtWidgets.QMessageBox

from aplicacion.dtos.proyecto import DtoClase
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


def test_anadir_clase_valida_aparece_en_dto_local(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases

    assert pagina.anadir_clase("Cliente") is True
    assert [clase.nombre for clase in pagina.dto_clases()] == ["Cliente"]


def test_no_permitir_clase_duplicada_en_ui(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases

    assert pagina.anadir_clase("Cliente") is True
    assert pagina.anadir_clase("Cliente") is False


def test_anadir_atributo_valido_en_dto(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases
    pagina.anadir_clase("Cliente")

    assert pagina.anadir_atributo(nombre_atributo="edad", tipo="int", obligatorio=False) is True
    atributo = pagina.dto_clases()[0].atributos[0]
    assert atributo.nombre == "edad"
    assert atributo.tipo == "int"


def test_establecer_desde_dto_recupera_estructura_esperada(wizard: WizardGeneradorProyectos) -> None:
    pagina = wizard.pagina_clases
    pagina.establecer_desde_dto([DtoClase(nombre="Cliente"), DtoClase(nombre="Pedido")])

    assert pagina.clases() == ["Cliente", "Pedido"]

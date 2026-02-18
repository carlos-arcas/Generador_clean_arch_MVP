"""Pruebas de DTO del wizard."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication

from aplicacion.dtos.proyecto import DtoAtributo, DtoClase, DtoProyectoEntrada
from infraestructura.bootstrap import construir_contenedor_aplicacion
from presentacion.wizard.wizard_generador import ControladorWizardProyecto, WizardGeneradorProyectos


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


def test_construir_dto_genera_dto_proyecto_entrada(app_qt: QApplication) -> None:
    wizard = crear_wizard(controlador=ControladorWizardProyecto())
    wizard.pagina_datos.campo_nombre.setText("MiProyecto")
    wizard.pagina_datos.campo_ruta.setText("/tmp/mi_proyecto")
    wizard.pagina_datos.campo_descripcion.setText("Descripción")
    wizard.pagina_datos.campo_version.setText("1.2.3")
    wizard.pagina_clases.establecer_desde_dto(
        [DtoClase(nombre="Cliente", atributos=[DtoAtributo(nombre="id", tipo="int", obligatorio=True)])]
    )

    dto = wizard._controlador.construir_dto(wizard)

    assert isinstance(dto.proyecto, DtoProyectoEntrada)
    assert dto.proyecto.nombre_proyecto == "MiProyecto"
    assert dto.proyecto.clases[0].nombre == "Cliente"


def test_modulo_wizard_no_importa_dominio() -> None:
    import inspect
    import presentacion.wizard.wizard_generador as modulo

    codigo = inspect.getsource(modulo)
    assert "from dominio" not in codigo
    assert "import dominio" not in codigo

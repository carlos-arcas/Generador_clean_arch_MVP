from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication

from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto
from dominio.preset.preset_proyecto import PresetProyecto
from presentacion.wizard.wizard_generador import WizardGeneradorProyectos


@pytest.fixture
def app_qt() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def test_wizard_aplica_preset_y_refresca_campos(app_qt: QApplication) -> None:
    wizard = WizardGeneradorProyectos()
    preset = PresetProyecto(
        nombre="api_basica",
        especificacion=EspecificacionProyecto(
            nombre_proyecto="ApiBasica",
            ruta_destino="/tmp/api",
            descripcion="API base",
            version="1.2.0",
            clases=[
                EspecificacionClase(
                    nombre="Pedido",
                    atributos=[EspecificacionAtributo(nombre="folio", tipo="str", obligatorio=True)],
                )
            ],
        ),
        blueprints=["base_clean_arch", "crud_json"],
        metadata={"persistencia": "SQLite"},
    )

    wizard.aplicar_preset(preset)

    assert wizard.pagina_datos.campo_nombre.text() == "ApiBasica"
    assert wizard.pagina_datos.campo_ruta.text() == "/tmp/api"
    assert wizard.pagina_persistencia.persistencia_seleccionada() == "SQLite"
    assert wizard.pagina_clases.clases() == ["Pedido"]
    assert "Clase: Pedido" in wizard.pagina_resumen.texto_resumen()

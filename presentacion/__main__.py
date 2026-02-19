"""Punto de entrada de la aplicación PySide6."""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from infraestructura.bootstrap import configurar_logging
from infraestructura.bootstrap.bootstrap_gui import construir_contenedor_gui
from presentacion.wizard.wizard_generador import WizardGeneradorProyectos

LOGGER = logging.getLogger(__name__)


def _capturar_excepciones_qt(exctype: type[BaseException], value: BaseException, tb) -> None:
    LOGGER.critical("Excepción no controlada en hilo principal Qt.", exc_info=(exctype, value, tb))
    sys.__excepthook__(exctype, value, tb)


def main() -> int:
    configurar_logging("logs")
    sys.excepthook = _capturar_excepciones_qt

    LOGGER.info("Inicializando aplicación PySide6 en modo wizard")
    contenedor = construir_contenedor_gui()
    app = QApplication(sys.argv)
    wizard = WizardGeneradorProyectos(
        generar_proyecto=contenedor.generar_proyecto_mvp,
        guardar_preset=contenedor.guardar_preset_proyecto,
        cargar_preset=contenedor.cargar_preset_proyecto,
        guardar_credencial=contenedor.guardar_credencial,
        catalogo_blueprints=contenedor.consultar_catalogo_blueprints.ejecutar(),
    )
    wizard.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

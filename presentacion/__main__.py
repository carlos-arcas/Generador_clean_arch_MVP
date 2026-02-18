"""Punto de entrada de la aplicación PySide6."""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from infraestructura.logging_config import configurar_logging
from presentacion.wizard.wizard_generador import WizardGeneradorProyectos

LOGGER = logging.getLogger(__name__)


def _capturar_excepciones_qt(exctype: type[BaseException], value: BaseException, tb) -> None:
    LOGGER.critical("Excepción no controlada en hilo principal Qt.", exc_info=(exctype, value, tb))
    sys.__excepthook__(exctype, value, tb)


def main() -> int:
    configurar_logging("logs")
    sys.excepthook = _capturar_excepciones_qt

    LOGGER.info("Inicializando aplicación PySide6 en modo wizard")
    app = QApplication(sys.argv)
    wizard = WizardGeneradorProyectos()
    wizard.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

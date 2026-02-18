"""Punto de entrada de la aplicación PySide6."""

from __future__ import annotations

import logging
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication

from infraestructura.logging_config import configurar_logging
from presentacion.ventana_principal import VentanaPrincipal

LOGGER = logging.getLogger(__name__)


def _capturar_excepciones_qt(exctype: type[BaseException], value: BaseException, tb) -> None:
    LOGGER.critical("Excepción no controlada en hilo principal Qt.", exc_info=(exctype, value, tb))
    sys.__excepthook__(exctype, value, tb)


def main() -> int:
    configurar_logging("logs")
    sys.excepthook = _capturar_excepciones_qt

    version_generador = Path("VERSION").read_text(encoding="utf-8").strip()

    LOGGER.info("Inicializando aplicación PySide6")
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal(version_generador=version_generador)
    ventana.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

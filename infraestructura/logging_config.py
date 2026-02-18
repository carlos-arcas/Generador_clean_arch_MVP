"""Configuración centralizada de logging con rotación y filtrado de secretos."""

from __future__ import annotations

from logging.handlers import RotatingFileHandler
import logging
from pathlib import Path
import sys


class FiltroSecretos(logging.Filter):
    """Filtra mensajes que podrían contener secretos básicos."""

    PALABRAS_SENSIBLES = ("password", "token", "secret")

    def filter(self, record: logging.LogRecord) -> bool:
        mensaje = record.getMessage().lower()
        if any(palabra in mensaje for palabra in self.PALABRAS_SENSIBLES):
            return False
        return True


def configurar_logging(ruta_logs: str) -> None:
    """Configura logging para seguimiento y errores críticos con rotación."""
    directorio_logs = Path(ruta_logs)
    directorio_logs.mkdir(parents=True, exist_ok=True)

    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s"
    )
    filtro_secretos = FiltroSecretos()

    logger_raiz = logging.getLogger()
    logger_raiz.setLevel(logging.DEBUG)
    logger_raiz.handlers.clear()

    seguimiento_handler = RotatingFileHandler(
        directorio_logs / "seguimiento.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    seguimiento_handler.setLevel(logging.DEBUG)
    seguimiento_handler.setFormatter(formato)
    seguimiento_handler.addFilter(filtro_secretos)

    crashes_handler = RotatingFileHandler(
        directorio_logs / "crashes.log",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    crashes_handler.setLevel(logging.ERROR)
    crashes_handler.setFormatter(formato)
    crashes_handler.addFilter(filtro_secretos)

    logger_raiz.addHandler(seguimiento_handler)
    logger_raiz.addHandler(crashes_handler)

    def capturar_excepcion_global(
        exctype: type[BaseException], value: BaseException, traceback
    ) -> None:
        if issubclass(exctype, KeyboardInterrupt):
            sys.__excepthook__(exctype, value, traceback)
            return
        logger_raiz.critical(
            "Excepción no controlada capturada por el manejador global.",
            exc_info=(exctype, value, traceback),
        )

    sys.excepthook = capturar_excepcion_global

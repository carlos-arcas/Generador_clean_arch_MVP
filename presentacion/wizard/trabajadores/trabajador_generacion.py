"""Trabajador QRunnable para ejecutar la generación MVP sin bloquear la UI."""

from __future__ import annotations

import logging
import traceback

from PySide6.QtCore import QObject, QRunnable, Signal

from aplicacion.casos_uso.generacion.generar_proyecto_mvp import (
    GenerarProyectoMvp,
    GenerarProyectoMvpEntrada,
    GenerarProyectoMvpSalida,
)

LOGGER = logging.getLogger(__name__)


class SenalesTrabajadorGeneracionMvp(QObject):
    """Señales para comunicar avance y resultado entre worker y wizard."""

    progreso = Signal(str)
    exito = Signal(object)
    error = Signal(str, str)


class TrabajadorGeneracionMvp(QRunnable):
    """Ejecuta el caso de uso GenerarProyectoMvp dentro de un QThreadPool."""

    def __init__(self, caso_uso: GenerarProyectoMvp, entrada: GenerarProyectoMvpEntrada) -> None:
        super().__init__()
        self._caso_uso = caso_uso
        self._entrada = entrada
        self.senales = SenalesTrabajadorGeneracionMvp()

    def run(self) -> None:
        try:
            self.senales.progreso.emit("Construyendo plan desde blueprints...")
            salida = self._caso_uso.ejecutar(self._entrada)
            self.senales.progreso.emit("Proyecto generado correctamente.")
            if not salida.valido:
                detalle = "\n".join(salida.errores) if salida.errores else "Sin detalles adicionales"
                LOGGER.warning("Generación completada con auditoría inválida: %s", detalle)
            self.senales.exito.emit(salida)
        except Exception as exc:  # pragma: no cover - protección adicional
            LOGGER.error("Excepción no controlada en trabajador MVP: %s", exc)
            detalle = traceback.format_exc()
            LOGGER.error("Stacktrace worker MVP:\n%s", detalle)
            self.senales.error.emit("Falló la generación (ver logs)", detalle)

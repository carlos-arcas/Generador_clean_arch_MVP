"""Trabajador QRunnable para ejecutar la generación MVP sin bloquear la UI."""

from __future__ import annotations

import logging
from pathlib import Path
import threading
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
    cancelado = Signal(str)
    error = Signal(str, str)


class TrabajadorGeneracionMvp(QRunnable):
    """Ejecuta el caso de uso GenerarProyectoMvp dentro de un QThreadPool."""

    def __init__(self, caso_uso: GenerarProyectoMvp, entrada: GenerarProyectoMvpEntrada) -> None:
        super().__init__()
        self._caso_uso = caso_uso
        self._entrada = entrada
        self._cancelacion = threading.Event()
        self.senales = SenalesTrabajadorGeneracionMvp()

    def cancelar(self) -> None:
        """Solicita la cancelación cooperativa del worker."""
        self._cancelacion.set()

    def cancelado(self) -> bool:
        """Indica si ya se recibió una solicitud de cancelación."""
        return self._cancelacion.is_set()

    def run(self) -> None:
        try:
            salida = self._caso_uso.ejecutar(
                self._entrada,
                reportar_progreso=self.senales.progreso.emit,
                debe_cancelar=self.cancelado,
            )
            if salida.cancelado:
                self.senales.cancelado.emit("Generación cancelada por el usuario.")
                return
            if not salida.valido:
                detalle = "\n".join(salida.errores) if salida.errores else "Sin detalles adicionales"
                LOGGER.warning("Generación completada con auditoría inválida: %s", detalle)
            self.senales.exito.emit(salida)
        except Exception as exc:  # pragma: no cover - protección adicional
            LOGGER.error("Excepción no controlada en trabajador MVP: %s", exc)
            detalle = traceback.format_exc()
            LOGGER.error("Stacktrace worker MVP:\n%s", detalle)
            self._registrar_crash(detalle)
            self.senales.error.emit("La generación falló.", detalle)

    def _registrar_crash(self, detalle: str) -> None:
        logs_dir = Path("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        crash_file = logs_dir / "crashes.log"
        with crash_file.open("a", encoding="utf-8") as file:
            file.write(f"\n{detalle}\n")

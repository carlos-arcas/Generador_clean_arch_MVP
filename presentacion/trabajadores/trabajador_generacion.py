"""Trabajador QRunnable para ejecutar la generación MVP sin bloquear la UI."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal

from aplicacion.errores import ErrorAplicacion, ErrorInfraestructura
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp, GenerarProyectoMvpEntrada
from presentacion.mapeo_mensajes_error import MensajeUxError, mapear_error_a_mensaje_ux
from presentacion.ux.id_incidente import generar_id_incidente

LOGGER = logging.getLogger(__name__)


class SenalesTrabajadorGeneracionMvp(QObject):
    """Señales para comunicar avance y resultado entre worker y wizard."""

    progreso = Signal(str)
    exito = Signal(object)
    error = Signal(object)


class TrabajadorGeneracionMvp(QRunnable):
    """Ejecuta el caso de uso GenerarProyectoMvp dentro de un QThreadPool."""

    def __init__(self, caso_uso: GenerarProyectoMvp, entrada: GenerarProyectoMvpEntrada) -> None:
        super().__init__()
        self._caso_uso = caso_uso
        self._entrada = entrada
        self._ruta_logs = Path("logs")
        self.senales = SenalesTrabajadorGeneracionMvp()

    def _emitir_error_mapeado(self, exc: Exception) -> None:
        id_incidente = generar_id_incidente()
        LOGGER.error("Fallo en trabajador de generación id_incidente=%s", id_incidente, exc_info=True)
        mensaje_ux: MensajeUxError = mapear_error_a_mensaje_ux(exc, id_incidente, self._ruta_logs)
        self.senales.error.emit(mensaje_ux)

    def run(self) -> None:
        try:
            self.senales.progreso.emit("Construyendo plan desde blueprints...")
            salida = self._caso_uso.ejecutar(self._entrada)
            self.senales.progreso.emit("Proyecto generado correctamente.")
            if not salida.valido:
                detalle = "\n".join(salida.errores) if salida.errores else "Sin detalles adicionales"
                LOGGER.warning("Generación completada con auditoría inválida: %s", detalle)
            self.senales.exito.emit(salida)
        except ErrorInfraestructura as exc:
            self._emitir_error_mapeado(exc)
        except ErrorAplicacion as exc:
            self._emitir_error_mapeado(exc)
        except OSError as exc:
            self._emitir_error_mapeado(exc)
        except ValueError as exc:
            self._emitir_error_mapeado(exc)

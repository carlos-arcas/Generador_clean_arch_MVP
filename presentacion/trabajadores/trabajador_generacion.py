"""Trabajador en segundo plano para ejecutar generación y auditoría."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import traceback

from PySide6.QtCore import QObject, QRunnable, Signal

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado, ResultadoAuditoria
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from dominio.modelos import EspecificacionProyecto

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResultadoGeneracion:
    """Resultado de alto nivel de la ejecución en background."""

    ruta_destino: str
    auditoria: ResultadoAuditoria


class SenalesTrabajadorGeneracion(QObject):
    """Canal de señales para reportar eventos del trabajador."""

    progreso = Signal(str)
    finalizado = Signal(object)
    error = Signal(object)


class TrabajadorGeneracion(QRunnable):
    """Ejecuta la cadena de casos de uso sin bloquear el hilo principal de UI."""

    def __init__(
        self,
        especificacion: EspecificacionProyecto,
        blueprints: list[str],
        crear_plan_desde_blueprints: CrearPlanDesdeBlueprints,
        ejecutar_plan: EjecutarPlan,
        auditor: AuditarProyectoGenerado,
        version_generador: str,
    ) -> None:
        super().__init__()
        self.senales = SenalesTrabajadorGeneracion()
        self._especificacion = especificacion
        self._blueprints = blueprints
        self._crear_plan = crear_plan_desde_blueprints
        self._ejecutar_plan = ejecutar_plan
        self._auditor = auditor
        self._version_generador = version_generador

    def run(self) -> None:
        try:
            self.senales.progreso.emit("Construyendo plan de generación...")
            plan = self._crear_plan.ejecutar(self._especificacion, self._blueprints)

            self.senales.progreso.emit("Ejecutando plan en disco...")
            self._ejecutar_plan.ejecutar(
                plan=plan,
                ruta_destino=self._especificacion.ruta_destino,
                opciones={"origen": "wizard_pyside6"},
                version_generador=self._version_generador,
                blueprints_usados=[f"{nombre}@1.0.0" for nombre in self._blueprints],
            )

            self.senales.progreso.emit("Ejecutando auditoría...")
            resultado_auditoria = self._auditor.ejecutar(
                self._especificacion.ruta_destino,
                blueprints_usados=self._blueprints,
            )
            LOGGER.info(
                "Resultado auditoría desde worker: valido=%s cobertura=%s resumen=%s errores=%s",
                resultado_auditoria.valido,
                resultado_auditoria.cobertura,
                resultado_auditoria.resumen,
                resultado_auditoria.lista_errores,
            )
            self.senales.finalizado.emit(
                ResultadoGeneracion(
                    ruta_destino=self._especificacion.ruta_destino,
                    auditoria=resultado_auditoria,
                )
            )
        except Exception as exc:  # pragma: no cover - cobertura vía tests de wiring
            LOGGER.error("Fallo en trabajador de generación: %s", exc)
            LOGGER.debug("Stacktrace worker:\n%s", traceback.format_exc())
            self.senales.error.emit(exc)

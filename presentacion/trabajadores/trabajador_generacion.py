"""Trabajador en segundo plano para ejecutar generación y auditoría."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import traceback

from PySide6.QtCore import QObject, QRunnable, Signal

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.dtos.auditoria.dto_auditoria_entrada import DtoAuditoriaEntrada
from aplicacion.dtos.auditoria.dto_auditoria_salida import DtoAuditoriaSalida
from aplicacion.casos_uso.actualizar_manifest_patch import ActualizarManifestPatch
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.crear_plan_patch_desde_blueprints import CrearPlanPatchDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from dominio.modelos import EspecificacionProyecto

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResultadoGeneracion:
    """Resultado de alto nivel de la ejecución en background."""

    ruta_destino: str
    auditoria: DtoAuditoriaSalida


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
        crear_plan_patch_desde_blueprints: CrearPlanPatchDesdeBlueprints,
        ejecutar_plan: EjecutarPlan,
        actualizar_manifest_patch: ActualizarManifestPatch,
        auditor: AuditarProyectoGenerado,
        version_generador: str,
    ) -> None:
        super().__init__()
        self.senales = SenalesTrabajadorGeneracion()
        self._especificacion = especificacion
        self._blueprints = blueprints
        self._crear_plan = crear_plan_desde_blueprints
        self._crear_plan_patch = crear_plan_patch_desde_blueprints
        self._ejecutar_plan = ejecutar_plan
        self._actualizar_manifest_patch = actualizar_manifest_patch
        self._auditor = auditor
        self._version_generador = version_generador

    def run(self) -> None:
        try:
            self.senales.progreso.emit("Construyendo plan de generación...")
            ruta_manifest = Path(self._especificacion.ruta_destino) / "manifest.json"
            modo_patch = ruta_manifest.exists()
            if modo_patch:
                LOGGER.info("Proyecto existente detectado. Se aplicará modo PATCH.")
                plan = self._crear_plan_patch.ejecutar(
                    self._especificacion,
                    self._especificacion.ruta_destino,
                )
            else:
                plan = self._crear_plan.ejecutar(self._especificacion, self._blueprints)

            self.senales.progreso.emit("Ejecutando plan en disco...")
            self._ejecutar_plan.ejecutar(
                plan=plan,
                ruta_destino=self._especificacion.ruta_destino,
                opciones={"origen": "wizard_pyside6"},
                version_generador=self._version_generador,
                blueprints_usados=[f"{nombre}@1.0.0" for nombre in self._blueprints],
                generar_manifest=not modo_patch,
            )
            if modo_patch:
                self._actualizar_manifest_patch.ejecutar(self._especificacion.ruta_destino, plan)

            self.senales.progreso.emit("Ejecutando auditoría...")
            resultado_auditoria = self._auditor.ejecutar(
                DtoAuditoriaEntrada(
                    ruta_proyecto=self._especificacion.ruta_destino,
                    blueprints_usados=self._blueprints,
                )
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

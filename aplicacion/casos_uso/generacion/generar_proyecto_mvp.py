"""Caso de uso MVP para generar proyecto funcional desde el wizard."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import shutil
from typing import Callable

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import (
    AuditarProyectoGenerado,
    ResultadoAuditoria,
)
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.puertos.sistema_archivos import SistemaArchivos
from dominio.excepciones.proyecto_ya_existe_error import ProyectoYaExisteError
from dominio.modelos import EspecificacionProyecto
from infraestructura.manifest.generador_manifest import GeneradorManifest

LOGGER = logging.getLogger(__name__)

DIRECTORIOS_BASE_MVP = [
    "dominio",
    "aplicacion",
    "infraestructura",
    "presentacion",
    "tests",
    "scripts",
    "docs",
    "logs",
    "configuracion",
]


@dataclass(frozen=True)
class GenerarProyectoMvpEntrada:
    """Entrada para ejecutar la generación MVP."""

    especificacion_proyecto: EspecificacionProyecto
    ruta_destino: str
    nombre_proyecto: str
    blueprints: list[str]


@dataclass(frozen=True)
class GenerarProyectoMvpSalida:
    """Resultado estructurado de la generación MVP."""

    ruta_generada: str
    archivos_generados: int
    valido: bool
    errores: list[str]
    warnings: list[str]
    auditoria: ResultadoAuditoria | None = None
    cancelado: bool = False


class CancelacionGeneracionError(Exception):
    """Indica que la generación fue cancelada por el usuario."""


class GenerarProyectoMvp:
    """Orquesta la generación de proyecto reutilizando casos de uso existentes."""

    def __init__(
        self,
        crear_plan_desde_blueprints: CrearPlanDesdeBlueprints,
        ejecutar_plan: EjecutarPlan,
        sistema_archivos: SistemaArchivos,
        generador_manifest: GeneradorManifest | None = None,
        auditor: AuditarProyectoGenerado | None = None,
    ) -> None:
        self._crear_plan = crear_plan_desde_blueprints
        self._ejecutar_plan = ejecutar_plan
        self._sistema_archivos = sistema_archivos
        self._generador_manifest = generador_manifest or GeneradorManifest()
        self._auditor = auditor or AuditarProyectoGenerado()

    def ejecutar(
        self,
        entrada: GenerarProyectoMvpEntrada,
        reportar_progreso: Callable[[str], None] | None = None,
        debe_cancelar: Callable[[], bool] | None = None,
    ) -> GenerarProyectoMvpSalida:
        """Genera el proyecto final en disco a partir de los blueprints MVP."""
        LOGGER.info(
            "Iniciando generación MVP para proyecto='%s' destino='%s' blueprints=%s",
            entrada.nombre_proyecto,
            entrada.ruta_destino,
            entrada.blueprints,
        )
        ruta_proyecto = Path(entrada.ruta_destino) / entrada.nombre_proyecto
        carpeta_existia = ruta_proyecto.exists()
        carpeta_creada_en_ejecucion = False
        reportar = reportar_progreso or (lambda *_: None)
        cancelar = debe_cancelar or (lambda: False)

        def _cancelar_si_corresponde() -> None:
            if cancelar():
                raise CancelacionGeneracionError("Generación cancelada por el usuario.")

        try:
            reportar("Validando ruta destino...")
            self._validar_ruta_destino(ruta_proyecto)
            _cancelar_si_corresponde()
            if not carpeta_existia:
                ruta_proyecto.mkdir(parents=True, exist_ok=False)
                carpeta_creada_en_ejecucion = True

            especificacion = entrada.especificacion_proyecto
            especificacion.nombre_proyecto = entrada.nombre_proyecto
            especificacion.ruta_destino = str(ruta_proyecto)
            especificacion.validar()

            blueprints_normalizados = [
                blueprint.removesuffix("_v1") if blueprint.endswith("_v1") else blueprint
                for blueprint in entrada.blueprints
            ]
            LOGGER.debug("Blueprints normalizados para ejecución: %s", blueprints_normalizados)

            reportar("Creando plan...")
            LOGGER.info("Etapa 1/3: asegurando estructura mínima de directorios")
            for directorio in DIRECTORIOS_BASE_MVP:
                self._sistema_archivos.asegurar_directorio(f"{ruta_proyecto}/{directorio}")
            _cancelar_si_corresponde()

            LOGGER.info("Etapa 2/3: creando plan compuesto")
            plan = self._crear_plan.ejecutar(especificacion, blueprints_normalizados)
            _cancelar_si_corresponde()

            reportar("Ejecutando plan...")
            LOGGER.info("Etapa 3/3: ejecutando plan en disco")
            archivos_creados = self._ejecutar_plan.ejecutar(
                plan=plan,
                ruta_destino=str(ruta_proyecto),
                opciones={"origen": "wizard_mvp"},
                blueprints_usados=[f"{nombre}@1.0.0" for nombre in blueprints_normalizados],
                generar_manifest=True,
            )
            _cancelar_si_corresponde()

            reportar("Generando manifest...")
            self._generador_manifest.generar(
                ruta_proyecto=str(ruta_proyecto),
                especificacion_proyecto=especificacion,
                blueprints=entrada.blueprints,
                archivos_generados=archivos_creados,
            )
            _cancelar_si_corresponde()

            reportar("Ejecutando auditoría...")
            resultado_auditoria = self._auditor.auditar(str(ruta_proyecto))
            LOGGER.info(
                "Auditoría post-generación: valido=%s errores=%s warnings=%s",
                resultado_auditoria.valido,
                len(resultado_auditoria.errores),
                len(resultado_auditoria.warnings),
            )
            salida = GenerarProyectoMvpSalida(
                ruta_generada=str(ruta_proyecto),
                archivos_generados=len(archivos_creados),
                valido=resultado_auditoria.valido,
                errores=resultado_auditoria.errores,
                warnings=resultado_auditoria.warnings,
                auditoria=resultado_auditoria,
            )
            LOGGER.info(
                "Generación MVP finalizada correctamente: ruta='%s' archivos=%s",
                salida.ruta_generada,
                salida.archivos_generados,
            )
            reportar("Finalizado")
            return salida
        except ProyectoYaExisteError:
            raise
        except CancelacionGeneracionError as exc:
            if carpeta_creada_en_ejecucion and ruta_proyecto.exists():
                shutil.rmtree(ruta_proyecto)
                LOGGER.info("Rollback por cancelación: eliminado directorio '%s'", ruta_proyecto)
            return GenerarProyectoMvpSalida(
                ruta_generada=str(ruta_proyecto),
                archivos_generados=0,
                valido=False,
                errores=[str(exc)],
                warnings=[],
                cancelado=True,
            )
        except Exception as exc:
            if carpeta_creada_en_ejecucion and ruta_proyecto.exists():
                shutil.rmtree(ruta_proyecto)
                LOGGER.info("Rollback ejecutado: eliminado directorio '%s'", ruta_proyecto)
            LOGGER.exception("Error al generar proyecto MVP.")
            return GenerarProyectoMvpSalida(
                ruta_generada=str(ruta_proyecto),
                archivos_generados=0,
                valido=False,
                errores=[str(exc)],
                warnings=[],
            )

    def _validar_ruta_destino(self, ruta_proyecto: Path) -> None:
        if not ruta_proyecto.exists():
            return
        if any(ruta_proyecto.iterdir()):
            raise ProyectoYaExisteError(
                f"La carpeta destino '{ruta_proyecto}' ya existe y no está vacía."
            )

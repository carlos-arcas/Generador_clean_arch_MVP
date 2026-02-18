"""Caso de uso MVP para generar proyecto funcional desde el wizard."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import shutil

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import (
    AuditarProyectoGenerado,
    ResultadoAuditoria,
)
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.puertos.generador_manifest_puerto import GeneradorManifestPuerto
from aplicacion.puertos.sistema_archivos import SistemaArchivos
from dominio.excepciones.proyecto_ya_existe_error import ProyectoYaExisteError
from dominio.especificacion import EspecificacionProyecto

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


class GenerarProyectoMvp:
    """Orquesta la generación de proyecto reutilizando casos de uso existentes."""

    def __init__(
        self,
        crear_plan_desde_blueprints: CrearPlanDesdeBlueprints,
        ejecutar_plan: EjecutarPlan,
        sistema_archivos: SistemaArchivos,
        generador_manifest: GeneradorManifestPuerto | None = None,
        auditor: AuditarProyectoGenerado | None = None,
    ) -> None:
        self._crear_plan = crear_plan_desde_blueprints
        self._ejecutar_plan = ejecutar_plan
        self._sistema_archivos = sistema_archivos
        self._generador_manifest = generador_manifest
        self._auditor = auditor or AuditarProyectoGenerado()

    def ejecutar(self, entrada: GenerarProyectoMvpEntrada) -> GenerarProyectoMvpSalida:
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

        try:
            self._validar_ruta_destino(ruta_proyecto)
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

            LOGGER.info("Etapa 1/3: asegurando estructura mínima de directorios")
            for directorio in DIRECTORIOS_BASE_MVP:
                self._sistema_archivos.asegurar_directorio(f"{ruta_proyecto}/{directorio}")

            LOGGER.info("Etapa 2/3: creando plan compuesto")
            plan = self._crear_plan.ejecutar(especificacion, blueprints_normalizados)

            LOGGER.info("Etapa 3/3: ejecutando plan en disco")
            archivos_creados = self._ejecutar_plan.ejecutar(
                plan=plan,
                ruta_destino=str(ruta_proyecto),
                opciones={"origen": "wizard_mvp"},
                blueprints_usados=[f"{nombre}@1.0.0" for nombre in blueprints_normalizados],
                generar_manifest=True,
            )
            if self._generador_manifest is not None:
                self._generador_manifest.generar(
                    ruta_proyecto=str(ruta_proyecto),
                    especificacion_proyecto=especificacion,
                    blueprints=entrada.blueprints,
                    archivos_generados=archivos_creados,
                )

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
            return salida
        except ProyectoYaExisteError:
            raise
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

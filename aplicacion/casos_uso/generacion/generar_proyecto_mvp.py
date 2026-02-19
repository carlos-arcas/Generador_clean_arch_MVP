"""Caso de uso MVP para generar proyecto funcional desde el wizard."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import (
    AuditarProyectoGenerado,
    ResultadoAuditoria,
)
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.pasos.ejecutar_auditoria import EjecutorAuditoriaGeneracion
from aplicacion.casos_uso.generacion.pasos.ejecutar_plan import EjecutorPlanGeneracion
from aplicacion.casos_uso.generacion.pasos.errores_pipeline import (
    ErrorAuditoriaGeneracion,
    ErrorEjecucionPlanGeneracion,
    ErrorNormalizacionEntradaGeneracion,
    ErrorPreparacionEstructuraGeneracion,
    ErrorPublicacionManifestGeneracion,
    ErrorValidacionEntradaGeneracion,
)
from aplicacion.casos_uso.generacion.pasos.normalizar_entrada import NormalizadorEntradaGeneracion
from aplicacion.casos_uso.generacion.pasos.preparar_estructura import PreparadorEstructuraGeneracion
from aplicacion.casos_uso.generacion.pasos.publicar_manifest import PublicadorManifestGeneracion
from aplicacion.casos_uso.generacion.pasos.rollback_generacion import RollbackGeneracion
from aplicacion.casos_uso.generacion.pasos.validar_entrada import ValidadorEntradaGeneracion
from aplicacion.puertos.generador_manifest_puerto import GeneradorManifestPuerto
from aplicacion.puertos.sistema_archivos import SistemaArchivos
from dominio.especificacion import EspecificacionProyecto

LOGGER = logging.getLogger(__name__)


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
        self._validador_entrada = ValidadorEntradaGeneracion()
        self._normalizador_entrada = NormalizadorEntradaGeneracion()
        self._preparador_estructura = PreparadorEstructuraGeneracion(sistema_archivos)
        self._ejecutor_plan = EjecutorPlanGeneracion(crear_plan_desde_blueprints, ejecutar_plan)
        self._publicador_manifest = PublicadorManifestGeneracion(generador_manifest)
        self._ejecutor_auditoria = EjecutorAuditoriaGeneracion(auditor or AuditarProyectoGenerado())
        self._rollback = RollbackGeneracion()

    def ejecutar(self, entrada: GenerarProyectoMvpEntrada) -> GenerarProyectoMvpSalida:
        """Genera el proyecto final en disco a partir de los blueprints MVP."""
        LOGGER.info(
            "Iniciando generación MVP para proyecto='%s' destino='%s' blueprints=%s",
            entrada.nombre_proyecto,
            entrada.ruta_destino,
            entrada.blueprints,
        )
        ruta_proyecto = self._validador_entrada.validar(entrada)
        entrada_normalizada = self._normalizador_entrada.normalizar(entrada, ruta_proyecto)

        carpeta_creada_en_ejecucion = False
        carpeta_existia_antes = ruta_proyecto.exists()
        try:
            carpeta_creada_en_ejecucion = self._preparador_estructura.preparar(ruta_proyecto)
            resultado_plan = self._ejecutor_plan.ejecutar(
                especificacion=entrada_normalizada.especificacion_proyecto,
                blueprints=entrada_normalizada.blueprints,
                ruta_proyecto=entrada_normalizada.ruta_proyecto,
            )
            self._publicador_manifest.publicar(
                ruta_proyecto=entrada_normalizada.ruta_proyecto,
                especificacion_proyecto=entrada_normalizada.especificacion_proyecto,
                blueprints=entrada.blueprints,
                archivos_generados=resultado_plan.archivos_creados,
            )
            resultado_auditoria = self._ejecutor_auditoria.ejecutar(entrada_normalizada.ruta_proyecto)
            return GenerarProyectoMvpSalida(
                ruta_generada=entrada_normalizada.ruta_proyecto,
                archivos_generados=len(resultado_plan.archivos_creados),
                valido=resultado_auditoria.valido,
                errores=resultado_auditoria.errores,
                warnings=resultado_auditoria.warnings,
                auditoria=resultado_auditoria,
            )
        except ErrorPreparacionEstructuraGeneracion as exc:
            self._rollback.ejecutar(ruta_proyecto, not carpeta_existia_antes)
            raise ErrorPreparacionEstructuraGeneracion(str(exc)) from exc
        except ErrorEjecucionPlanGeneracion as exc:
            self._rollback.ejecutar(ruta_proyecto, carpeta_creada_en_ejecucion)
            raise ErrorEjecucionPlanGeneracion(str(exc)) from exc
        except ErrorPublicacionManifestGeneracion as exc:
            self._rollback.ejecutar(ruta_proyecto, carpeta_creada_en_ejecucion)
            raise ErrorPublicacionManifestGeneracion(str(exc)) from exc
        except ErrorAuditoriaGeneracion as exc:
            self._rollback.ejecutar(ruta_proyecto, carpeta_creada_en_ejecucion)
            raise ErrorAuditoriaGeneracion(str(exc)) from exc
        except ErrorValidacionEntradaGeneracion:
            raise
        except ErrorNormalizacionEntradaGeneracion:
            raise

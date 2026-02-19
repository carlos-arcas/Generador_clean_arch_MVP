"""Bootstrap de dependencias para el contexto CLI."""

from __future__ import annotations

from dataclasses import dataclass

from aplicacion.casos_uso.actualizar_manifest_patch import ActualizarManifestPatch
from aplicacion.casos_uso.auditar_finalizacion_proyecto import AuditarFinalizacionProyecto
from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado as AuditarProyectoGeneradoArquitectura
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.crear_plan_patch_desde_blueprints import CrearPlanPatchDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp
from aplicacion.casos_uso.generar_manifest import GenerarManifest
from aplicacion.casos_uso.presets import CargarPresetProyecto
from aplicacion.casos_uso.validar_compatibilidad_blueprints import ValidarCompatibilidadBlueprints
from infraestructura.blueprints.metadata_registry import obtener_metadata_blueprints
from infraestructura.manifest.generador_manifest import GeneradorManifest
from infraestructura.planificador_blueprints_real import PlanificadorBlueprintsReal

from .bootstrap_base import _construir_puertos_infraestructura, _construir_repositorios_infraestructura


@dataclass(frozen=True)
class ContenedorCli:
    """Casos de uso requeridos por la interfaz CLI."""

    crear_plan_desde_blueprints: CrearPlanDesdeBlueprints
    crear_plan_patch_desde_blueprints: CrearPlanPatchDesdeBlueprints
    ejecutar_plan: EjecutarPlan
    actualizar_manifest_patch: ActualizarManifestPatch
    cargar_preset_proyecto: CargarPresetProyecto
    generar_proyecto_mvp: GenerarProyectoMvp
    auditar_proyecto: AuditarProyectoGenerado
    auditar_finalizacion_proyecto: AuditarFinalizacionProyecto


def construir_contenedor_cli() -> ContenedorCli:
    """Construye un contenedor mínimo para ejecución por línea de comandos."""

    puertos = _construir_puertos_infraestructura()
    repositorios = _construir_repositorios_infraestructura()

    crear_plan_desde_blueprints = CrearPlanDesdeBlueprints(
        repositorios.repositorio_blueprints,
        descubridor_plugins=puertos.descubridor_plugins,
    )
    generar_manifest = GenerarManifest(puertos.calculadora_hash)
    ejecutar_plan = EjecutarPlan(
        sistema_archivos=puertos.sistema_archivos,
        generador_manifest=generar_manifest,
    )

    auditor_proyecto = AuditarProyectoGenerado(puertos.ejecutor_procesos)
    auditor_arquitectura = AuditarProyectoGeneradoArquitectura()
    metadata_blueprints = obtener_metadata_blueprints()

    return ContenedorCli(
        crear_plan_desde_blueprints=crear_plan_desde_blueprints,
        crear_plan_patch_desde_blueprints=CrearPlanPatchDesdeBlueprints(
            lector_manifest=puertos.lector_manifest,
            crear_plan_desde_blueprints=crear_plan_desde_blueprints,
        ),
        ejecutar_plan=ejecutar_plan,
        actualizar_manifest_patch=ActualizarManifestPatch(
            lector_manifest=puertos.lector_manifest,
            escritor_manifest=puertos.escritor_manifest,
            calculadora_hash=puertos.calculadora_hash,
        ),
        cargar_preset_proyecto=CargarPresetProyecto(repositorios.repositorio_presets),
        generar_proyecto_mvp=GenerarProyectoMvp(
            crear_plan_desde_blueprints=crear_plan_desde_blueprints,
            ejecutar_plan=ejecutar_plan,
            sistema_archivos=puertos.sistema_archivos,
            generador_manifest=GeneradorManifest(),
        ),
        auditar_proyecto=auditor_proyecto,
        auditar_finalizacion_proyecto=AuditarFinalizacionProyecto(
            planificador_blueprints=PlanificadorBlueprintsReal(crear_plan_desde_blueprints),
            generar_proyecto_mvp=GenerarProyectoMvp(
                crear_plan_desde_blueprints=crear_plan_desde_blueprints,
                ejecutar_plan=ejecutar_plan,
                sistema_archivos=puertos.sistema_archivos,
                generador_manifest=GeneradorManifest(),
            ),
            auditor_arquitectura=auditor_arquitectura,
            ejecutor_procesos=puertos.ejecutor_procesos,
            validador_compatibilidad_blueprints=ValidarCompatibilidadBlueprints(metadata_blueprints),
        ),
    )

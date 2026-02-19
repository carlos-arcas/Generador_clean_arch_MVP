"""Funciones base de ensamblado técnico para los bootstrap por contexto."""

from __future__ import annotations

from dataclasses import dataclass

from aplicacion.casos_uso.actualizar_manifest_patch import ActualizarManifestPatch
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.crear_plan_patch_desde_blueprints import CrearPlanPatchDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generar_manifest import GenerarManifest
from aplicacion.casos_uso.presets import CargarPresetProyecto, GuardarPresetProyecto
from aplicacion.casos_uso.seguridad import GuardarCredencial
from infraestructura.calculadora_hash_real import CalculadoraHashReal
from infraestructura.ejecutor_procesos_subprocess import EjecutorProcesosSubprocess
from infraestructura.manifest_en_disco import EscritorManifestSeguro, LectorManifestEnDisco
from infraestructura.plugins.descubridor_plugins import DescubridorPlugins
from infraestructura.presets.repositorio_presets_json import RepositorioPresetsJson
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.seguridad import SelectorRepositorioCredenciales
from infraestructura.sistema_archivos_real import SistemaArchivosReal


@dataclass(frozen=True)
class PuertosInfraestructura:
    sistema_archivos: SistemaArchivosReal
    descubridor_plugins: DescubridorPlugins
    calculadora_hash: CalculadoraHashReal
    lector_manifest: LectorManifestEnDisco
    escritor_manifest: EscritorManifestSeguro
    ejecutor_procesos: EjecutorProcesosSubprocess


@dataclass(frozen=True)
class RepositoriosInfraestructura:
    repositorio_blueprints: RepositorioBlueprintsEnDisco
    repositorio_presets: RepositorioPresetsJson


@dataclass(frozen=True)
class AdaptadoresAplicacion:
    crear_plan_desde_blueprints: CrearPlanDesdeBlueprints
    crear_plan_patch_desde_blueprints: CrearPlanPatchDesdeBlueprints
    generar_manifest: GenerarManifest
    ejecutar_plan: EjecutarPlan
    actualizar_manifest_patch: ActualizarManifestPatch
    guardar_preset_proyecto: GuardarPresetProyecto
    cargar_preset_proyecto: CargarPresetProyecto
    guardar_credencial: GuardarCredencial


def _construir_puertos_infraestructura() -> PuertosInfraestructura:
    return PuertosInfraestructura(
        sistema_archivos=SistemaArchivosReal(),
        descubridor_plugins=DescubridorPlugins("plugins"),
        calculadora_hash=CalculadoraHashReal(),
        lector_manifest=LectorManifestEnDisco(),
        escritor_manifest=EscritorManifestSeguro(),
        ejecutor_procesos=EjecutorProcesosSubprocess(),
    )


def _construir_repositorios_infraestructura() -> RepositoriosInfraestructura:
    return RepositoriosInfraestructura(
        repositorio_blueprints=RepositorioBlueprintsEnDisco("blueprints"),
        repositorio_presets=RepositorioPresetsJson(),
    )


def _construir_adaptadores_aplicacion(
    puertos: PuertosInfraestructura,
    repositorios: RepositoriosInfraestructura,
) -> AdaptadoresAplicacion:
    crear_plan_desde_blueprints = CrearPlanDesdeBlueprints(
        repositorios.repositorio_blueprints,
        descubridor_plugins=puertos.descubridor_plugins,
    )
    generar_manifest = GenerarManifest(puertos.calculadora_hash)

    return AdaptadoresAplicacion(
        crear_plan_desde_blueprints=crear_plan_desde_blueprints,
        crear_plan_patch_desde_blueprints=CrearPlanPatchDesdeBlueprints(
            lector_manifest=puertos.lector_manifest,
            crear_plan_desde_blueprints=crear_plan_desde_blueprints,
        ),
        generar_manifest=generar_manifest,
        ejecutar_plan=EjecutarPlan(
            sistema_archivos=puertos.sistema_archivos,
            generador_manifest=generar_manifest,
        ),
        actualizar_manifest_patch=ActualizarManifestPatch(
            lector_manifest=puertos.lector_manifest,
            escritor_manifest=puertos.escritor_manifest,
            calculadora_hash=puertos.calculadora_hash,
        ),
        guardar_preset_proyecto=GuardarPresetProyecto(repositorios.repositorio_presets),
        cargar_preset_proyecto=CargarPresetProyecto(repositorios.repositorio_presets),
        guardar_credencial=GuardarCredencial(SelectorRepositorioCredenciales().crear()),
    )

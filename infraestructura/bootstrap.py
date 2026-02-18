"""Composition root de infraestructura para ensamblar la aplicación."""

from __future__ import annotations

from dataclasses import dataclass

from aplicacion.casos_uso.actualizar_manifest_patch import ActualizarManifestPatch
from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.crear_plan_patch_desde_blueprints import CrearPlanPatchDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp
from aplicacion.casos_uso.generar_manifest import GenerarManifest
from aplicacion.casos_uso.presets import CargarPresetProyecto, GuardarPresetProyecto
from aplicacion.casos_uso.seguridad import GuardarCredencial
from infraestructura.calculadora_hash_real import CalculadoraHashReal
from infraestructura.ejecutor_procesos_subprocess import EjecutorProcesosSubprocess
from infraestructura.logging_config import configurar_logging
from infraestructura.manifest.generador_manifest import GeneradorManifest as GeneradorManifestReal
from infraestructura.manifest_en_disco import EscritorManifestSeguro, LectorManifestEnDisco
from infraestructura.plugins.descubridor_plugins import DescubridorPlugins as DescubridorPluginsReal
from infraestructura.presets.repositorio_presets_json import RepositorioPresetsJson
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.seguridad import SelectorRepositorioCredenciales
from infraestructura.sistema_archivos_real import SistemaArchivosReal


@dataclass(frozen=True)
class ContenedorAplicacion:
    """Instancias de casos de uso y servicios listas para presentación."""

    crear_plan_desde_blueprints: CrearPlanDesdeBlueprints
    crear_plan_patch_desde_blueprints: CrearPlanPatchDesdeBlueprints
    generar_proyecto_mvp: GenerarProyectoMvp
    auditar_proyecto_generado: AuditarProyectoGenerado
    ejecutar_plan: EjecutarPlan
    actualizar_manifest_patch: ActualizarManifestPatch
    guardar_preset_proyecto: GuardarPresetProyecto
    cargar_preset_proyecto: CargarPresetProyecto
    guardar_credencial: GuardarCredencial
    catalogo_blueprints: list[tuple[str, str, str]]


def _construir_catalogo_blueprints(
    repositorio_blueprints: RepositorioBlueprintsEnDisco,
    descubridor_plugins: DescubridorPluginsReal,
) -> list[tuple[str, str, str]]:
    internos = [
        (blueprint.nombre(), blueprint.version(), "Blueprint interno")
        for blueprint in repositorio_blueprints.listar_blueprints()
    ]
    externos = [
        (plugin.nombre, plugin.version, plugin.descripcion)
        for plugin in descubridor_plugins.listar_plugins()
    ]
    catalogo_unico: dict[str, tuple[str, str, str]] = {
        nombre: (nombre, version, descripcion)
        for nombre, version, descripcion in [*internos, *externos]
    }
    return sorted(catalogo_unico.values(), key=lambda item: item[0])


def construir_contenedor_aplicacion() -> ContenedorAplicacion:
    """Construye el contenedor de aplicación inyectando adaptadores concretos."""

    descubridor_plugins = DescubridorPluginsReal("plugins")
    calculadora_hash = CalculadoraHashReal()
    sistema_archivos = SistemaArchivosReal()
    repositorio_blueprints = RepositorioBlueprintsEnDisco("blueprints")
    repositorio_presets = RepositorioPresetsJson()
    lector_manifest = LectorManifestEnDisco()
    escritor_manifest = EscritorManifestSeguro()
    ejecutor_procesos = EjecutorProcesosSubprocess()

    crear_plan_desde_blueprints = CrearPlanDesdeBlueprints(
        repositorio_blueprints=repositorio_blueprints,
        descubridor_plugins=descubridor_plugins,
    )
    crear_plan_patch_desde_blueprints = CrearPlanPatchDesdeBlueprints(
        lector_manifest=lector_manifest,
        crear_plan_desde_blueprints=crear_plan_desde_blueprints,
    )
    generar_manifest = GenerarManifest(calculadora_hash)
    ejecutar_plan = EjecutarPlan(
        sistema_archivos=sistema_archivos,
        generador_manifest=generar_manifest,
    )
    actualizar_manifest_patch = ActualizarManifestPatch(
        lector_manifest=lector_manifest,
        escritor_manifest=escritor_manifest,
        calculadora_hash=calculadora_hash,
    )
    guardar_preset_proyecto = GuardarPresetProyecto(repositorio_presets)
    cargar_preset_proyecto = CargarPresetProyecto(repositorio_presets)
    guardar_credencial = GuardarCredencial(SelectorRepositorioCredenciales().crear())
    auditar_proyecto_generado = AuditarProyectoGenerado(
        ejecutor_procesos=ejecutor_procesos,
        calculadora_hash=calculadora_hash,
    )
    generar_proyecto_mvp = GenerarProyectoMvp(
        crear_plan_desde_blueprints=crear_plan_desde_blueprints,
        ejecutar_plan=ejecutar_plan,
        sistema_archivos=sistema_archivos,
        generador_manifest=GeneradorManifestReal(),
    )

    return ContenedorAplicacion(
        crear_plan_desde_blueprints=crear_plan_desde_blueprints,
        crear_plan_patch_desde_blueprints=crear_plan_patch_desde_blueprints,
        generar_proyecto_mvp=generar_proyecto_mvp,
        auditar_proyecto_generado=auditar_proyecto_generado,
        ejecutar_plan=ejecutar_plan,
        actualizar_manifest_patch=actualizar_manifest_patch,
        guardar_preset_proyecto=guardar_preset_proyecto,
        cargar_preset_proyecto=cargar_preset_proyecto,
        guardar_credencial=guardar_credencial,
        catalogo_blueprints=_construir_catalogo_blueprints(repositorio_blueprints, descubridor_plugins),
    )


__all__ = ["ContenedorAplicacion", "construir_contenedor_aplicacion", "configurar_logging"]

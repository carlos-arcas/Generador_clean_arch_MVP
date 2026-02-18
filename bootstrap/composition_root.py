"""Composition root de la aplicación.

Centraliza el wiring de infraestructura y la construcción de casos de uso.
"""

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
from infraestructura.manifest.generador_manifest import GeneradorManifest as GeneradorManifestMvp
from infraestructura.manifest_en_disco import EscritorManifestSeguro, LectorManifestEnDisco
from infraestructura.plugins.descubridor_plugins import DescubridorPlugins
from infraestructura.presets.repositorio_presets_json import RepositorioPresetsJson
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.seguridad import SelectorRepositorioCredenciales
from infraestructura.sistema_archivos_real import SistemaArchivosReal


@dataclass(frozen=True)
class ContenedorAplicacion:
    """Dependencias construidas y listas para usar en presentación."""

    # Adaptadores / repositorios / servicios
    sistema_archivos: SistemaArchivosReal
    descubridor_plugins: DescubridorPlugins
    generador_manifest_mvp: GeneradorManifestMvp
    calculadora_hash: CalculadoraHashReal
    repositorio_blueprints: RepositorioBlueprintsEnDisco
    repositorio_presets: RepositorioPresetsJson
    lector_manifest: LectorManifestEnDisco
    escritor_manifest: EscritorManifestSeguro
    ejecutor_procesos: EjecutorProcesosSubprocess

    # Casos de uso
    crear_plan_desde_blueprints: CrearPlanDesdeBlueprints
    crear_plan_patch_desde_blueprints: CrearPlanPatchDesdeBlueprints
    generar_manifest: GenerarManifest
    ejecutar_plan: EjecutarPlan
    actualizar_manifest_patch: ActualizarManifestPatch
    generar_proyecto_mvp: GenerarProyectoMvp
    auditar_proyecto_generado: AuditarProyectoGenerado
    guardar_preset_proyecto: GuardarPresetProyecto
    cargar_preset_proyecto: CargarPresetProyecto
    guardar_credencial: GuardarCredencial

    # Datos auxiliares para UI
    catalogo_blueprints: list[tuple[str, str, str]]


def _construir_catalogo_blueprints(
    repositorio_blueprints: RepositorioBlueprintsEnDisco,
    descubridor_plugins: DescubridorPlugins,
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


def crear_contenedor() -> ContenedorAplicacion:
    """Construye y devuelve un contenedor con casos de uso, repositorios, adaptadores y servicios."""

    sistema_archivos = SistemaArchivosReal()
    descubridor_plugins = DescubridorPlugins("plugins")
    generador_manifest_mvp = GeneradorManifestMvp()
    calculadora_hash = CalculadoraHashReal()

    repositorio_blueprints = RepositorioBlueprintsEnDisco("blueprints")
    repositorio_presets = RepositorioPresetsJson()
    lector_manifest = LectorManifestEnDisco()
    escritor_manifest = EscritorManifestSeguro()
    ejecutor_procesos = EjecutorProcesosSubprocess()

    crear_plan_desde_blueprints = CrearPlanDesdeBlueprints(
        repositorio_blueprints,
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
    auditar_proyecto_generado = AuditarProyectoGenerado(ejecutor_procesos, calculadora_hash=calculadora_hash)
    generar_proyecto_mvp = GenerarProyectoMvp(
        crear_plan_desde_blueprints=crear_plan_desde_blueprints,
        ejecutar_plan=ejecutar_plan,
        sistema_archivos=sistema_archivos,
        generador_manifest=generador_manifest_mvp,
        auditor=auditar_proyecto_generado,
    )

    return ContenedorAplicacion(
        sistema_archivos=sistema_archivos,
        descubridor_plugins=descubridor_plugins,
        generador_manifest_mvp=generador_manifest_mvp,
        calculadora_hash=calculadora_hash,
        repositorio_blueprints=repositorio_blueprints,
        repositorio_presets=repositorio_presets,
        lector_manifest=lector_manifest,
        escritor_manifest=escritor_manifest,
        ejecutor_procesos=ejecutor_procesos,
        crear_plan_desde_blueprints=crear_plan_desde_blueprints,
        crear_plan_patch_desde_blueprints=crear_plan_patch_desde_blueprints,
        generar_manifest=generar_manifest,
        ejecutar_plan=ejecutar_plan,
        actualizar_manifest_patch=actualizar_manifest_patch,
        generar_proyecto_mvp=generar_proyecto_mvp,
        auditar_proyecto_generado=auditar_proyecto_generado,
        guardar_preset_proyecto=guardar_preset_proyecto,
        cargar_preset_proyecto=cargar_preset_proyecto,
        guardar_credencial=guardar_credencial,
        catalogo_blueprints=_construir_catalogo_blueprints(
            repositorio_blueprints=repositorio_blueprints,
            descubridor_plugins=descubridor_plugins,
        ),
    )


__all__ = ["ContenedorAplicacion", "crear_contenedor", "configurar_logging"]

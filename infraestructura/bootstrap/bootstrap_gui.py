"""Bootstrap de dependencias para el contexto GUI (wizard)."""

from __future__ import annotations

from dataclasses import dataclass

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.consultar_catalogo_blueprints import ConsultarCatalogoBlueprints
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp
from aplicacion.dtos.blueprints import DtoBlueprintMetadata
from infraestructura.blueprints.metadata_registry import obtener_metadata_blueprints
from infraestructura.manifest.generador_manifest import GeneradorManifest

from .bootstrap_base import (
    _construir_adaptadores_aplicacion,
    _construir_puertos_infraestructura,
    _construir_repositorios_infraestructura,
)


@dataclass(frozen=True)
class ContenedorGui:
    """Casos de uso requeridos por la aplicación GUI."""

    generar_proyecto_mvp: GenerarProyectoMvp
    guardar_preset_proyecto: object
    cargar_preset_proyecto: object
    guardar_credencial: object
    consultar_catalogo_blueprints: ConsultarCatalogoBlueprints
    metadata_blueprints: dict[str, DtoBlueprintMetadata]


def construir_contenedor_gui() -> ContenedorGui:
    """Construye un contenedor mínimo para ejecución en wizard gráfico."""

    puertos = _construir_puertos_infraestructura()
    repositorios = _construir_repositorios_infraestructura()
    adaptadores = _construir_adaptadores_aplicacion(puertos=puertos, repositorios=repositorios)

    return ContenedorGui(
        generar_proyecto_mvp=GenerarProyectoMvp(
            crear_plan_desde_blueprints=adaptadores.crear_plan_desde_blueprints,
            ejecutar_plan=adaptadores.ejecutar_plan,
            sistema_archivos=puertos.sistema_archivos,
            generador_manifest=GeneradorManifest(),
            auditor=AuditarProyectoGenerado(),
        ),
        guardar_preset_proyecto=adaptadores.guardar_preset_proyecto,
        cargar_preset_proyecto=adaptadores.cargar_preset_proyecto,
        guardar_credencial=adaptadores.guardar_credencial,
        consultar_catalogo_blueprints=ConsultarCatalogoBlueprints(
            repositorio_blueprints=repositorios.repositorio_blueprints,
            descubridor_plugins=puertos.descubridor_plugins,
        ),
        metadata_blueprints=obtener_metadata_blueprints(),
    )

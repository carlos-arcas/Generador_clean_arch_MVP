"""Puntos de entrada de bootstrap por contexto de presentación."""

from __future__ import annotations

from dataclasses import dataclass

from infraestructura.logging_config import configurar_logging

from .bootstrap_cli import ContenedorCli, construir_contenedor_cli
from .bootstrap_gui import ContenedorGui, construir_contenedor_gui


@dataclass(frozen=True)
class ContenedorAplicacion:
    """Wrapper legado que expone contratos históricos para pruebas existentes."""

    crear_plan_desde_blueprints: object
    crear_plan_patch_desde_blueprints: object
    ejecutar_plan: object
    actualizar_manifest_patch: object
    generar_proyecto_mvp: object
    auditar_proyecto_generado: object
    guardar_preset_proyecto: object
    cargar_preset_proyecto: object
    guardar_credencial: object
    catalogo_blueprints: list[tuple[str, str, str]]


def construir_contenedor_aplicacion() -> ContenedorAplicacion:
    """Construye un contenedor legado desde los bootstrap por contexto."""

    contenedor_cli = construir_contenedor_cli()
    contenedor_gui = construir_contenedor_gui()
    return ContenedorAplicacion(
        crear_plan_desde_blueprints=contenedor_cli.crear_plan_desde_blueprints,
        crear_plan_patch_desde_blueprints=contenedor_cli.crear_plan_patch_desde_blueprints,
        ejecutar_plan=contenedor_cli.ejecutar_plan,
        actualizar_manifest_patch=contenedor_cli.actualizar_manifest_patch,
        generar_proyecto_mvp=contenedor_gui.generar_proyecto_mvp,
        auditar_proyecto_generado=contenedor_cli.auditar_proyecto,
        guardar_preset_proyecto=contenedor_gui.guardar_preset_proyecto,
        cargar_preset_proyecto=contenedor_gui.cargar_preset_proyecto,
        guardar_credencial=contenedor_gui.guardar_credencial,
        catalogo_blueprints=contenedor_gui.consultar_catalogo_blueprints.ejecutar(),
    )


__all__ = [
    "ContenedorAplicacion",
    "ContenedorCli",
    "ContenedorGui",
    "configurar_logging",
    "construir_contenedor_aplicacion",
    "construir_contenedor_cli",
    "construir_contenedor_gui",
]

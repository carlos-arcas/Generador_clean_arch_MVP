"""Descubridor de plugins de blueprints externos en disco."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path

from aplicacion.puertos.blueprint import Blueprint
from dominio.modelos import ArchivoGenerado, EspecificacionProyecto, PlanGeneracion

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class MetadataPlugin:
    """Metadata normalizada de un plugin externo."""

    nombre: str
    version: str
    descripcion: str
    compatible_con: list[str]
    capas: list[str]
    requiere: list[str]
    ruta_plugin: Path


class BlueprintPluginExterno(Blueprint):
    """Blueprint dinámico generado desde estructura de plugin en disco."""

    def __init__(self, metadata: MetadataPlugin) -> None:
        self._metadata = metadata

    @property
    def metadata(self) -> MetadataPlugin:
        return self._metadata

    def nombre(self) -> str:
        return self._metadata.nombre

    def version(self) -> str:
        return self._metadata.version

    def validar(self, especificacion: EspecificacionProyecto) -> None:
        especificacion.validar()

    def generar_plan(self, especificacion: EspecificacionProyecto) -> PlanGeneracion:
        self.validar(especificacion)
        ruta_templates = self._metadata.ruta_plugin / "templates"
        if not ruta_templates.exists() or not ruta_templates.is_dir():
            raise ValueError(
                f"El plugin '{self._metadata.nombre}' no contiene carpeta templates/."
            )

        archivos: list[ArchivoGenerado] = []
        for archivo in ruta_templates.rglob("*"):
            if not archivo.is_file():
                continue
            ruta_relativa = archivo.relative_to(ruta_templates).as_posix()
            contenido = archivo.read_text(encoding="utf-8")
            archivos.append(ArchivoGenerado(ruta_relativa=ruta_relativa, contenido_texto=contenido))

        if not archivos:
            raise ValueError(f"El plugin '{self._metadata.nombre}' no contiene templates requeridos.")

        plan = PlanGeneracion(archivos=archivos)
        plan.validar_sin_conflictos()
        return plan


class DescubridorPlugins:
    """Gestiona descubrimiento y carga segura de plugins externos."""

    def __init__(self, ruta_plugins: str = "plugins") -> None:
        self._ruta_plugins = Path(ruta_plugins)

    def listar_plugins(self) -> list[MetadataPlugin]:
        plugins: list[MetadataPlugin] = []
        if not self._ruta_plugins.exists():
            return plugins

        for carpeta in self._ruta_plugins.iterdir():
            if not carpeta.is_dir() or carpeta.name.startswith("__"):
                continue
            metadata = self._cargar_metadata(carpeta)
            if metadata is None:
                continue
            plugins.append(metadata)
        return sorted(plugins, key=lambda plugin: plugin.nombre)

    def cargar_plugin(self, nombre: str) -> BlueprintPluginExterno:
        for metadata in self.listar_plugins():
            if metadata.nombre == nombre:
                return BlueprintPluginExterno(metadata)
        raise ValueError(f"Plugin no encontrado: {nombre}")

    def _cargar_metadata(self, ruta_plugin: Path) -> MetadataPlugin | None:
        archivo_blueprint = ruta_plugin / "blueprint.json"
        if not archivo_blueprint.exists():
            LOGGER.warning("Plugin ignorado sin blueprint.json: %s", ruta_plugin)
            return None

        try:
            payload = json.loads(archivo_blueprint.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            LOGGER.warning("Plugin inválido en %s: %s", ruta_plugin, exc)
            return None

        requeridos = ["nombre", "version", "descripcion", "compatible_con", "capas", "requiere"]
        faltantes = [clave for clave in requeridos if clave not in payload]
        if faltantes:
            LOGGER.warning("Plugin inválido '%s': faltan campos %s", ruta_plugin.name, faltantes)
            return None

        try:
            return MetadataPlugin(
                nombre=str(payload["nombre"]),
                version=str(payload["version"]),
                descripcion=str(payload["descripcion"]),
                compatible_con=[str(item) for item in payload["compatible_con"]],
                capas=[str(item) for item in payload["capas"]],
                requiere=[str(item) for item in payload["requiere"]],
                ruta_plugin=ruta_plugin,
            )
        except TypeError as exc:
            LOGGER.warning("Plugin inválido '%s': %s", ruta_plugin.name, exc)
            return None

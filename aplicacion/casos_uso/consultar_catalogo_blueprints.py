"""Caso de uso para consultar catálogo de blueprints disponibles."""

from __future__ import annotations

from aplicacion.puertos.blueprint import RepositorioBlueprints
from aplicacion.puertos.descubridor_plugins_puerto import DescubridorPluginsPuerto


class ConsultarCatalogoBlueprints:
    """Devuelve catálogo unificado de blueprints internos y plugins."""

    def __init__(
        self,
        repositorio_blueprints: RepositorioBlueprints,
        descubridor_plugins: DescubridorPluginsPuerto,
    ) -> None:
        self._repositorio_blueprints = repositorio_blueprints
        self._descubridor_plugins = descubridor_plugins

    def ejecutar(self) -> list[tuple[str, str, str]]:
        internos = [
            (blueprint.nombre(), blueprint.version(), "Blueprint interno")
            for blueprint in self._repositorio_blueprints.listar_blueprints()
        ]
        externos = [
            (plugin.nombre, plugin.version, plugin.descripcion)
            for plugin in self._descubridor_plugins.listar_plugins()
        ]
        catalogo_unico: dict[str, tuple[str, str, str]] = {
            nombre: (nombre, version, descripcion)
            for nombre, version, descripcion in [*internos, *externos]
        }
        return sorted(catalogo_unico.values(), key=lambda item: item[0])

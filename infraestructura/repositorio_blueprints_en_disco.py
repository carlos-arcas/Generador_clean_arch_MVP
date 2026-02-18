"""Repositorio de blueprints basado en módulos Python en disco."""

from __future__ import annotations

import importlib
from pathlib import Path

from aplicacion.puertos.blueprint import Blueprint, RepositorioBlueprints


class RepositorioBlueprintsEnDisco(RepositorioBlueprints):
    """Carga blueprints desde un directorio `blueprints` del proyecto."""

    def __init__(self, ruta_blueprints: str = "blueprints") -> None:
        self._ruta_blueprints = Path(ruta_blueprints)

    def listar_blueprints(self) -> list[Blueprint]:
        blueprints: list[Blueprint] = []
        if not self._ruta_blueprints.exists():
            return blueprints

        for carpeta in self._ruta_blueprints.iterdir():
            if not carpeta.is_dir() or carpeta.name.startswith("__"):
                continue
            if not (carpeta / "blueprint.py").exists():
                continue
            modulo = f"{self._ruta_blueprints.name}.{carpeta.name}.blueprint"
            clase_blueprint = self._resolver_clase_blueprint(modulo)
            if clase_blueprint is None:
                continue
            blueprints.append(clase_blueprint())
        return blueprints

    def obtener_por_nombre(self, nombre: str) -> Blueprint:
        for blueprint in self.listar_blueprints():
            if blueprint.nombre() == nombre:
                return blueprint
        raise ValueError(f"Blueprint no encontrado: {nombre}")

    def _resolver_clase_blueprint(self, modulo: str) -> type[Blueprint] | None:
        modulo_obj = importlib.import_module(modulo)
        for atributo in vars(modulo_obj).values():
            if (
                isinstance(atributo, type)
                and issubclass(atributo, Blueprint)
                and atributo is not Blueprint
                and atributo.__module__ == modulo
            ):
                return atributo
        return None

"""Puertos para blueprints de generación de proyectos."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from dominio.modelos import EspecificacionProyecto, PlanGeneracion


class Blueprint(ABC):
    """Contrato para una unidad versionada de generación de plan."""

    @abstractmethod
    def nombre(self) -> str:
        """Nombre único del blueprint."""

    @abstractmethod
    def version(self) -> str:
        """Versión semántica del blueprint."""

    @abstractmethod
    def validar(self, especificacion: EspecificacionProyecto) -> None:
        """Valida que la especificación sea compatible."""

    @abstractmethod
    def generar_plan(self, especificacion: EspecificacionProyecto) -> PlanGeneracion:
        """Genera un plan parcial a partir de la especificación."""


class RepositorioBlueprints(ABC):
    """Contrato de acceso a blueprints disponibles en el sistema."""

    @abstractmethod
    def listar_blueprints(self) -> list[Blueprint]:
        """Retorna el catálogo de blueprints registrados."""

    @abstractmethod
    def obtener_por_nombre(self, nombre: str) -> Blueprint:
        """Obtiene un blueprint por su nombre único."""


class DescubridorPlugins(Protocol):
    """Contrato para localizar blueprints externos instalados como plugins."""

    def cargar_plugin(self, nombre: str) -> Blueprint:
        """Carga un blueprint de plugin por su nombre."""

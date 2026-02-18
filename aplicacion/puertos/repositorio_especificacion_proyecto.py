"""Puerto para la persistencia de especificaciones del proyecto."""

from __future__ import annotations

from abc import ABC, abstractmethod

from dominio.modelos import EspecificacionProyecto


class RepositorioEspecificacionProyecto(ABC):
    """Define operaciones de acceso a la especificación del proyecto."""

    @abstractmethod
    def obtener(self) -> EspecificacionProyecto:
        """Obtiene la especificación actual."""

    @abstractmethod
    def guardar(self, especificacion: EspecificacionProyecto) -> None:
        """Guarda la especificación actualizada."""

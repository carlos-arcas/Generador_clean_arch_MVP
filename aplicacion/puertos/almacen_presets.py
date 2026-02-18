"""Puerto para persistencia de presets reutilizables."""

from __future__ import annotations

from abc import ABC, abstractmethod


class AlmacenPresets(ABC):
    """Abstracción para guardar/cargar presets."""

    @abstractmethod
    def guardar(self, nombre: str, contenido_json: dict) -> str:
        """Guarda un preset y retorna la ruta escrita."""

    @abstractmethod
    def cargar(self, ruta: str) -> dict:
        """Carga el contenido JSON de un preset."""

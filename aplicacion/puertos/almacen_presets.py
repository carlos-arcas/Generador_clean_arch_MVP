"""Puerto para persistencia de presets reutilizables."""

from __future__ import annotations

from abc import ABC, abstractmethod

from dominio.preset.preset_proyecto import PresetProyecto


class AlmacenPresets(ABC):
    """Abstracción para guardar/cargar/listar presets."""

    @abstractmethod
    def guardar(self, preset: PresetProyecto, ruta: str | None = None) -> str:
        """Guarda un preset y retorna la ruta escrita."""

    @abstractmethod
    def cargar(self, nombre_preset: str) -> PresetProyecto:
        """Carga un preset por nombre."""

    @abstractmethod
    def listar(self) -> list[str]:
        """Lista nombres de presets disponibles."""

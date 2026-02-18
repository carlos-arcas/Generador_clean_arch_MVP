"""Entidad de dominio para presets reutilizables de configuración de proyecto."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dominio.modelos import EspecificacionProyecto


@dataclass
class PresetProyecto:
    """Configuración reusable para generar proyectos desde wizard o CLI."""

    nombre: str
    especificacion: "EspecificacionProyecto"
    blueprints: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def validar(self) -> None:
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del preset no puede estar vacío.")
        self.especificacion.validar()
        if not self.blueprints:
            raise ValueError("El preset debe incluir al menos un blueprint.")

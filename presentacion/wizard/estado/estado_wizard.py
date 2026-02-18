"""Estado interno del wizard de generación de proyectos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EstadoWizardProyecto:
    """Agrupa estado mutable del wizard para reducir acoplamiento entre capas de UI."""

    especificacion_proyecto: Any
    generar_proyecto: Any
    guardar_preset: Any
    cargar_preset: Any
    guardar_credencial: Any
    catalogo_blueprints: list[tuple[str, str, str]]
    trabajador_activo: Any = None

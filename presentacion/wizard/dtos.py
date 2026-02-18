"""DTOs de presentación para recopilar datos del wizard."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DatosWizardProyecto:
    """Representa la configuración capturada por el wizard."""

    nombre: str
    ruta: str
    descripcion: str
    version: str
    clases: list[str]
    persistencia: str

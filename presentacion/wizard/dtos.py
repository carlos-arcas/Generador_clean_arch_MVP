"""DTOs de presentación para recopilar datos del wizard."""

from __future__ import annotations

from dataclasses import dataclass

from presentacion.wizard.modelos.modelo_clases_temporal import ClaseTemporal


@dataclass(frozen=True)
class DatosWizardProyecto:
    """Representa la configuración capturada por el wizard."""

    nombre: str
    ruta: str
    descripcion: str
    version: str
    clases: list[ClaseTemporal]
    persistencia: str

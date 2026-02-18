"""DTOs de presentación para recopilar datos del wizard."""

from __future__ import annotations

from dataclasses import dataclass

from dominio.modelos import EspecificacionProyecto


@dataclass(frozen=True)
class DatosWizardProyecto:
    """Representa la configuración capturada por el wizard."""

    nombre: str
    ruta: str
    descripcion: str
    version: str
    especificacion_proyecto: EspecificacionProyecto
    persistencia: str

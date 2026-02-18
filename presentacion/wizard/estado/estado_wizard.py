"""DTOs de estado del wizard de generación."""

from __future__ import annotations

from dataclasses import dataclass

from aplicacion.dtos.proyecto import DtoClase


@dataclass(frozen=True)
class EstadoWizardProyecto:
    """Estado serializable del wizard para construir el DTO final."""

    nombre: str
    ruta: str
    descripcion: str
    version: str
    clases: list[DtoClase]
    persistencia: str
    usuario_credencial: str
    secreto_credencial: str
    guardar_credencial: bool

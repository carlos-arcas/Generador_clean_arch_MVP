"""DTOs de presentación para recopilar datos del wizard."""

from __future__ import annotations

from dataclasses import dataclass, field

from aplicacion.dtos.proyecto import DtoProyectoEntrada


@dataclass(frozen=True)
class DatosWizardProyecto:
    """Representa la configuración capturada por el wizard."""

    nombre: str
    ruta: str
    descripcion: str
    version: str
    proyecto: DtoProyectoEntrada
    persistencia: str
    usuario_credencial: str = ""
    secreto_credencial: str = field(default="", repr=False)
    guardar_credencial: bool = False

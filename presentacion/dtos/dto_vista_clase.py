"""DTO de vista para clases sin dependencias de dominio ni framework UI."""

from __future__ import annotations

from dataclasses import dataclass, field

from presentacion.dtos.dto_vista_atributo import DtoVistaAtributo


@dataclass(frozen=True)
class DtoVistaClase:
    """Representa una clase plana para consumo de la capa de presentación."""

    nombre: str
    atributos: list[DtoVistaAtributo] = field(default_factory=list)

"""DTO de entrada para clases del proyecto."""

from __future__ import annotations

from dataclasses import dataclass, field

from aplicacion.dtos.proyecto.dto_atributo import DtoAtributo


@dataclass(frozen=True)
class DtoClase:
    """Representa una clase con su lista de atributos."""

    nombre: str
    atributos: list[DtoAtributo] = field(default_factory=list)

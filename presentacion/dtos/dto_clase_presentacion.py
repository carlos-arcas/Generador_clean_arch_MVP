"""DTO de presentación para clases sin dependencias de dominio."""

from __future__ import annotations

from dataclasses import dataclass, field

from presentacion.dtos.dto_atributo_presentacion import DtoAtributoPresentacion


@dataclass(frozen=True)
class DtoClasePresentacion:
    """Representa una clase para consumo de widgets/modelos de Qt."""

    nombre: str
    atributos: list[DtoAtributoPresentacion] = field(default_factory=list)

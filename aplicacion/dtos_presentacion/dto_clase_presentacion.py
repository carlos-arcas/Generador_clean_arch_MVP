"""DTO de presentación para clases sin dependencias de dominio ni framework UI."""

from __future__ import annotations

from dataclasses import dataclass, field

from aplicacion.dtos_presentacion.dto_atributo_presentacion import DtoAtributoPresentacion


@dataclass(frozen=True)
class DtoClasePresentacion:
    """Representa una clase plana para consumo de la capa de presentación."""

    nombre: str
    atributos: list[DtoAtributoPresentacion] = field(default_factory=list)

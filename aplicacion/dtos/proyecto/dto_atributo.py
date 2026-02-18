"""DTO de entrada para atributos del proyecto."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DtoAtributo:
    """Representa un atributo sin dependencia de dominio."""

    nombre: str
    tipo: str
    obligatorio: bool = False

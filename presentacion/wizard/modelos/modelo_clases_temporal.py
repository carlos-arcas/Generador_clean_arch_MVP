"""Modelos temporales para representar clases y atributos en el wizard."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AtributoTemporal:
    """Representa un atributo capturado desde la UI del wizard."""

    nombre: str
    tipo: str
    obligatorio: bool = False


@dataclass
class ClaseTemporal:
    """Representa una clase capturada desde la UI del wizard."""

    nombre: str
    atributos: list[AtributoTemporal] = field(default_factory=list)

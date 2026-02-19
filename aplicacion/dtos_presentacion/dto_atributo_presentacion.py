"""DTO de presentación para atributos sin dependencias de dominio ni framework UI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DtoAtributoPresentacion:
    """Representa un atributo plano para la capa de presentación."""

    nombre: str
    tipo: str
    obligatorio: bool = False
    valor_por_defecto: str = ""

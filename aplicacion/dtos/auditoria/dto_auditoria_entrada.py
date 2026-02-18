"""DTO de entrada para la auditoría del proyecto generado."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DtoAuditoriaEntrada:
    """Parámetros de entrada requeridos por el caso de uso de auditoría."""

    ruta_proyecto: str
    blueprints_usados: list[str] = field(default_factory=list)

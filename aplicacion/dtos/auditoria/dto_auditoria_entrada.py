"""DTO de entrada del caso de uso de auditoría de proyecto."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DtoAuditoriaEntrada:
    """Datos necesarios para ejecutar la auditoría de un proyecto generado."""

    ruta_proyecto: str
    blueprints_usados: list[str] = field(default_factory=list)

"""DTO de salida del caso de uso de auditoría de proyecto."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DtoAuditoriaSalida:
    """Resultado estructurado de la auditoría del proyecto."""

    valido: bool
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
    cobertura: float | None = None
    resumen: str = ""

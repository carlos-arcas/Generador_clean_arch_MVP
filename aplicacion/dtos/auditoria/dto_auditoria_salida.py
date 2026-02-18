"""DTO de salida para la auditoría del proyecto generado."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DtoAuditoriaSalida:
    """Resultado consolidado de la auditoría del proyecto."""

    valido: bool
    lista_errores: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    cobertura: float | None = None
    resumen: str = ""

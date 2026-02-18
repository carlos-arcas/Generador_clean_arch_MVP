"""Generador de DTO de salida de auditoría."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ResultadoAuditoria:
    """Resultado de la auditoría automática post-generación."""

    errores: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valido(self) -> bool:
        return not self.errores


class GeneradorReporteAuditoria:
    """Construye el resultado final de auditoría."""

    def generar(self, errores: list[str], warnings: list[str]) -> ResultadoAuditoria:
        return ResultadoAuditoria(errores=errores, warnings=warnings)

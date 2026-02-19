"""Contratos compartidos para validadores de auditoría."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ContextoAuditoria:
    """Información disponible para cada validador de auditoría."""

    base: Path


@dataclass(frozen=True)
class ResultadoValidacion:
    """Resultado estándar de una regla de auditoría."""

    exito: bool
    errores: list[str] = field(default_factory=list)


class ValidadorAuditoria(ABC):
    """Contrato base para validadores de auditoría."""

    @abstractmethod
    def validar(self, contexto: ContextoAuditoria) -> ResultadoValidacion:
        """Ejecuta la validación y devuelve errores encontrados."""

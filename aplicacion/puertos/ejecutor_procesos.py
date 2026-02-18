"""Puerto para ejecución de procesos externos."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoProceso:
    """Resultado de la ejecución de un proceso externo."""

    codigo_salida: int
    stdout: str
    stderr: str


class EjecutorProcesos(ABC):
    """Contrato para ejecutar comandos fuera del proceso principal."""

    @abstractmethod
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        """Ejecuta un comando y devuelve el resultado capturado."""

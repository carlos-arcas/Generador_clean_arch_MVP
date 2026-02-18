"""Puerto para cálculo de hash de archivos."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class CalculadoraHashPuerto(Protocol):
    """Contrato para cálculo de hash sobre archivos."""

    def calcular_hash_archivo(self, ruta: Path) -> str:
        """Calcula hash del archivo indicado por ruta."""

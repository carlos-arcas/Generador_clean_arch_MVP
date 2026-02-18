"""Puerto para cálculo de hashes criptográficos."""

from __future__ import annotations

from abc import ABC, abstractmethod


class CalculadoraHash(ABC):
    """Contrato para cálculo SHA256 sobre archivos del proyecto."""

    @abstractmethod
    def calcular_sha256(self, ruta_absoluta: str) -> str:
        """Calcula SHA256 del archivo en una ruta absoluta."""

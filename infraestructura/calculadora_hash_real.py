"""Implementación real de cálculo de hash SHA256."""

from __future__ import annotations

import hashlib

from aplicacion.puertos.calculadora_hash import CalculadoraHash


class CalculadoraHashReal(CalculadoraHash):
    """Calcula hashes SHA256 leyendo bytes del sistema de archivos."""

    def calcular_sha256(self, ruta_absoluta: str) -> str:
        digestor = hashlib.sha256()
        with open(ruta_absoluta, "rb") as archivo:
            for bloque in iter(lambda: archivo.read(8192), b""):
                digestor.update(bloque)
        return digestor.hexdigest()

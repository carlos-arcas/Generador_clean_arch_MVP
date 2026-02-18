"""Validación de consistencia de hashes en manifest para auditoría CLI."""

from __future__ import annotations

import hashlib
from pathlib import Path

from aplicacion.puertos.calculadora_hash import CalculadoraHash


class CalculadoraHashInterna(CalculadoraHash):
    """Implementación local para evitar dependencia directa a infraestructura."""

    def calcular_sha256(self, ruta_absoluta: str) -> str:
        ruta = Path(ruta_absoluta)
        return hashlib.sha256(ruta.read_bytes()).hexdigest()


class VerificadorHashes:
    """Valida integridad de archivos declarados en manifest."""

    def __init__(self, calculadora_hash: CalculadoraHash) -> None:
        self._calculadora_hash = calculadora_hash

    def validar_consistencia_manifest(self, base: Path, payload_manifest: dict) -> list[str]:
        errores: list[str] = []
        for entrada in payload_manifest.get("archivos", []):
            ruta_relativa = entrada.get("ruta_relativa", "")
            hash_esperado = entrada.get("hash_sha256", "")
            if not ruta_relativa or not hash_esperado:
                errores.append("manifest.json contiene entradas incompletas.")
                continue
            ruta_archivo = base / ruta_relativa
            if not ruta_archivo.exists():
                errores.append(f"manifest.json referencia archivo inexistente: {ruta_relativa}")
                continue
            hash_actual = self._calculadora_hash.calcular_sha256(str(ruta_archivo))
            if hash_actual != hash_esperado:
                errores.append(f"Hash inconsistente para {ruta_relativa} en manifest.json")
        return errores

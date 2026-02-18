"""Verificador de integridad mínima de manifest para auditoría."""

from __future__ import annotations

import json
from pathlib import Path


class VerificadorHashes:
    """Valida presencia y formato JSON del MANIFEST del proyecto."""

    def verificar(self, base: Path) -> list[str]:
        candidatos = [base / "MANIFEST.json", base / "configuracion" / "MANIFEST.json", base / "manifest.json"]
        ruta_manifest = next((ruta for ruta in candidatos if ruta.exists()), None)
        if ruta_manifest is None:
            return ["No existe MANIFEST requerido: MANIFEST.json"]

        try:
            payload = json.loads(ruta_manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return [f"{ruta_manifest.name} no es un JSON válido: {exc}"]

        if not isinstance(payload, dict):
            return [f"{ruta_manifest.name} debe contener un objeto JSON en raíz."]

        return []

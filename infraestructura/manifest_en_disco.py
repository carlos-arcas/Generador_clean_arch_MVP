"""Adaptadores de infraestructura para leer y escribir manifest.json."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import tempfile

from aplicacion.puertos.manifest import EscritorManifest, LectorManifest
from dominio.modelos import EntradaManifest, ManifestProyecto


class LectorManifestEnDisco(LectorManifest):
    """Lee manifest.json desde un proyecto generado."""

    def leer(self, ruta_proyecto: str) -> ManifestProyecto:
        ruta_manifest = Path(ruta_proyecto) / "manifest.json"
        if not ruta_manifest.exists():
            raise FileNotFoundError(f"No existe manifest.json en {ruta_proyecto}")
        payload = json.loads(ruta_manifest.read_text(encoding="utf-8"))
        entradas = [EntradaManifest(**entrada) for entrada in payload.get("archivos", [])]
        return ManifestProyecto(
            version_generador=payload["version_generador"],
            blueprints_usados=payload.get("blueprints_usados", []),
            archivos=entradas,
            timestamp_generacion=payload["timestamp_generacion"],
            opciones=payload.get("opciones", {}),
        )


class EscritorManifestSeguro(EscritorManifest):
    """Persiste manifest.json con reemplazo atómico."""

    def escribir(self, ruta_proyecto: str, manifest: ManifestProyecto) -> None:
        ruta_proyecto_path = Path(ruta_proyecto)
        ruta_proyecto_path.mkdir(parents=True, exist_ok=True)
        ruta_manifest = ruta_proyecto_path / "manifest.json"
        payload = {
            "version_generador": manifest.version_generador,
            "blueprints_usados": manifest.blueprints_usados,
            "archivos": [asdict(entrada) for entrada in manifest.archivos],
            "timestamp_generacion": manifest.timestamp_generacion,
            "opciones": manifest.opciones,
        }

        descriptor, ruta_temporal = tempfile.mkstemp(
            dir=str(ruta_proyecto_path),
            prefix=".manifest.",
            suffix=".tmp",
        )
        ruta_temporal_path = Path(ruta_temporal)
        try:
            with open(descriptor, "w", encoding="utf-8", closefd=True) as archivo_temp:
                json.dump(payload, archivo_temp, ensure_ascii=False, indent=2)
            ruta_temporal_path.replace(ruta_manifest)
        finally:
            if ruta_temporal_path.exists():
                ruta_temporal_path.unlink()

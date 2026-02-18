"""Caso de uso para generar el manifest del proyecto generado."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any

from aplicacion.puertos.calculadora_hash import CalculadoraHash
from dominio.manifest import EntradaManifest, ManifestProyecto
from dominio.plan_generacion import PlanGeneracion

LOGGER = logging.getLogger(__name__)


class GenerarManifest:
    """Construye y persiste manifest.json con hashes de archivos generados."""

    def __init__(self, calculadora_hash: CalculadoraHash) -> None:
        self._calculadora_hash = calculadora_hash

    def ejecutar(
        self,
        plan: PlanGeneracion,
        ruta_destino: str,
        opciones: dict[str, Any],
        version_generador: str,
        blueprints_usados: list[str],
    ) -> ManifestProyecto:
        """Calcula hashes, crea el manifest y lo escribe en disco."""
        entradas: list[EntradaManifest] = []
        ruta_base = Path(ruta_destino)

        for archivo in plan.archivos:
            ruta_absoluta = ruta_base / archivo.ruta_relativa
            hash_sha = self._calculadora_hash.calcular_sha256(str(ruta_absoluta))
            LOGGER.info("Hash calculado para %s: %s", archivo.ruta_relativa, hash_sha)
            entradas.append(
                EntradaManifest(ruta_relativa=archivo.ruta_relativa, hash_sha256=hash_sha)
            )

        manifest = ManifestProyecto(
            version_generador=version_generador,
            blueprints_usados=blueprints_usados,
            archivos=entradas,
            timestamp_generacion=datetime.now(timezone.utc).isoformat(),
            opciones=opciones,
        )
        self._escribir_manifest(manifest, ruta_base / "manifest.json")
        return manifest

    def _escribir_manifest(self, manifest: ManifestProyecto, ruta_manifest: Path) -> None:
        payload = {
            "version_generador": manifest.version_generador,
            "blueprints_usados": manifest.blueprints_usados,
            "archivos": [asdict(entrada) for entrada in manifest.archivos],
            "timestamp_generacion": manifest.timestamp_generacion,
            "opciones": manifest.opciones,
        }
        ruta_manifest.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

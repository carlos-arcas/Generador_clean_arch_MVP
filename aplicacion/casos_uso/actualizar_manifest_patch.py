"""Caso de uso para actualizar manifest tras generación incremental PATCH."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from pathlib import Path

from aplicacion.puertos.calculadora_hash import CalculadoraHash
from aplicacion.puertos.manifest import EscritorManifest, LectorManifest
from dominio.manifest import EntradaManifest, ManifestProyecto
from dominio.plan_generacion import PlanGeneracion

LOGGER = logging.getLogger(__name__)


class ActualizarManifestPatch:
    """Anexa solo nuevas entradas al manifest existente."""

    def __init__(
        self,
        lector_manifest: LectorManifest,
        escritor_manifest: EscritorManifest,
        calculadora_hash: CalculadoraHash,
    ) -> None:
        self._lector_manifest = lector_manifest
        self._escritor_manifest = escritor_manifest
        self._calculadora_hash = calculadora_hash

    def ejecutar(self, ruta_proyecto: str, plan_archivos_nuevos: PlanGeneracion) -> ManifestProyecto:
        manifest_actual = self._lector_manifest.leer(ruta_proyecto)
        nuevas_entradas: list[EntradaManifest] = []
        base = Path(ruta_proyecto)

        for archivo in plan_archivos_nuevos.archivos:
            ruta_absoluta = base / archivo.ruta_relativa
            hash_sha = self._calculadora_hash.calcular_sha256(str(ruta_absoluta))
            LOGGER.info("PATCH: hash calculado para %s", archivo.ruta_relativa)
            nuevas_entradas.append(
                EntradaManifest(ruta_relativa=archivo.ruta_relativa, hash_sha256=hash_sha)
            )

        manifest_actualizado = ManifestProyecto(
            version_generador=manifest_actual.version_generador,
            blueprints_usados=manifest_actual.blueprints_usados,
            archivos=[*manifest_actual.archivos, *nuevas_entradas],
            timestamp_generacion=datetime.now(timezone.utc).isoformat(),
            opciones=manifest_actual.opciones,
        )
        self._escritor_manifest.escribir(ruta_proyecto, manifest_actualizado)
        LOGGER.info("PATCH: manifest actualizado con %s nuevas entradas", len(nuevas_entradas))
        return manifest_actualizado


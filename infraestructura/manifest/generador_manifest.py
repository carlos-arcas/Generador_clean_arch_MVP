"""Generación de MANIFEST.json para trazabilidad del proyecto MVP."""

from __future__ import annotations

import json
from pathlib import Path

from dominio.especificacion import EspecificacionProyecto


class GeneradorManifest:
    """Construye `configuracion/MANIFEST.json` con metadata mínima reproducible."""

    def generar(
        self,
        ruta_proyecto: str,
        especificacion_proyecto: EspecificacionProyecto,
        blueprints: list[str],
        archivos_generados: list[str],
    ) -> None:
        """Escribe MANIFEST.json con versión, blueprints, clases y total de archivos."""
        ruta_base = Path(ruta_proyecto)
        ruta_manifest = ruta_base / "configuracion" / "MANIFEST.json"
        ruta_manifest.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "version_generador": self._leer_version_generador(),
            "blueprints": blueprints,
            "clases": [
                {
                    "nombre": clase.nombre,
                    "atributos": [atributo.nombre for atributo in clase.atributos],
                }
                for clase in especificacion_proyecto.clases
            ],
            "archivos_generados": len(archivos_generados),
        }
        ruta_manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _leer_version_generador(self) -> str:
        ruta_version = Path(__file__).resolve().parents[2] / "VERSION"
        if not ruta_version.exists():
            return "0.0.0"
        return ruta_version.read_text(encoding="utf-8").strip()

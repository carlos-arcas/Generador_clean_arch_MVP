"""Persistencia de presets en disco bajo configuracion/presets."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile

from aplicacion.puertos.almacen_presets import AlmacenPresets


class AlmacenPresetsDisco(AlmacenPresets):
    """Guarda/carga presets JSON con escritura atómica."""

    def __init__(self, directorio_presets: str = "configuracion/presets") -> None:
        self._directorio = Path(directorio_presets)

    def guardar(self, nombre: str, contenido_json: dict) -> str:
        self._directorio.mkdir(parents=True, exist_ok=True)
        ruta_destino = self._directorio / f"{nombre}.json"
        descriptor, ruta_temporal = tempfile.mkstemp(
            dir=str(self._directorio),
            prefix=f".{nombre}.",
            suffix=".tmp",
        )
        ruta_temporal_path = Path(ruta_temporal)
        try:
            with open(descriptor, "w", encoding="utf-8", closefd=True) as archivo_temp:
                json.dump(contenido_json, archivo_temp, ensure_ascii=False, indent=2)
            ruta_temporal_path.replace(ruta_destino)
        finally:
            if ruta_temporal_path.exists():
                ruta_temporal_path.unlink()
        return str(ruta_destino)

    def cargar(self, ruta: str) -> dict:
        ruta_preset = Path(ruta)
        if not ruta_preset.exists():
            raise FileNotFoundError(f"No existe el preset en la ruta: {ruta}")
        return json.loads(ruta_preset.read_text(encoding="utf-8"))

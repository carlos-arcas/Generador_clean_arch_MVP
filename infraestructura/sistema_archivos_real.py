"""Implementación real del puerto de sistema de archivos."""

from __future__ import annotations

from pathlib import Path
import tempfile

from aplicacion.puertos.sistema_archivos import SistemaArchivos


class SistemaArchivosReal(SistemaArchivos):
    """Escribe archivos y crea directorios usando el sistema de archivos local."""

    def escribir_texto_atomico(self, ruta_absoluta: str, contenido: str) -> None:
        ruta_destino = Path(ruta_absoluta)
        self.asegurar_directorio(str(ruta_destino.parent))

        descriptor, ruta_temporal = tempfile.mkstemp(
            dir=str(ruta_destino.parent), prefix=f".{ruta_destino.name}.", suffix=".tmp"
        )
        ruta_temporal_path = Path(ruta_temporal)
        try:
            with open(descriptor, "w", encoding="utf-8", closefd=True) as archivo_temp:
                archivo_temp.write(contenido)
            ruta_temporal_path.replace(ruta_destino)
        finally:
            if ruta_temporal_path.exists():
                ruta_temporal_path.unlink()

    def asegurar_directorio(self, ruta_absoluta: str) -> None:
        Path(ruta_absoluta).mkdir(parents=True, exist_ok=True)

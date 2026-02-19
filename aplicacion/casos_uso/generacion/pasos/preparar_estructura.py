"""Paso para preparar la estructura base de carpetas del proyecto."""

from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.generacion.pasos.errores_pipeline import ErrorPreparacionEstructuraGeneracion
from aplicacion.puertos.sistema_archivos import SistemaArchivos

DIRECTORIOS_BASE_MVP = [
    "dominio",
    "aplicacion",
    "infraestructura",
    "presentacion",
    "tests",
    "scripts",
    "docs",
    "logs",
    "configuracion",
]


class PreparadorEstructuraGeneracion:
    """Crea la carpeta raíz y directorios base del proyecto."""

    def __init__(self, sistema_archivos: SistemaArchivos) -> None:
        self._sistema_archivos = sistema_archivos

    def preparar(self, ruta_proyecto: Path) -> bool:
        carpeta_creada_en_ejecucion = False
        try:
            if not ruta_proyecto.exists():
                ruta_proyecto.mkdir(parents=True, exist_ok=False)
                carpeta_creada_en_ejecucion = True

            for directorio in DIRECTORIOS_BASE_MVP:
                self._sistema_archivos.asegurar_directorio(f"{ruta_proyecto}/{directorio}")
            return carpeta_creada_en_ejecucion
        except OSError as exc:
            raise ErrorPreparacionEstructuraGeneracion(
                f"No se pudo preparar la estructura del proyecto en '{ruta_proyecto}'."
            ) from exc

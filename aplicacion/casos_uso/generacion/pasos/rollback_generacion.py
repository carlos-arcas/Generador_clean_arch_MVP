"""Paso para rollback en errores del pipeline de generación."""

from __future__ import annotations

from pathlib import Path
import shutil


class RollbackGeneracion:
    """Elimina carpeta de proyecto si fue creada durante la ejecución."""

    def ejecutar(self, ruta_proyecto: Path, carpeta_creada_en_ejecucion: bool) -> bool:
        if not carpeta_creada_en_ejecucion or not ruta_proyecto.exists():
            return False
        shutil.rmtree(ruta_proyecto)
        return True

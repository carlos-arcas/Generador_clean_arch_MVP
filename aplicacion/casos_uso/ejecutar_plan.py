"""Caso de uso para ejecutar un plan de generación de archivos."""

from __future__ import annotations

from pathlib import Path

from aplicacion.puertos.sistema_archivos import SistemaArchivos
from dominio.modelos import PlanGeneracion


class EjecutarPlan:
    """Aplica un plan de generación usando el puerto de sistema de archivos."""

    def __init__(self, sistema_archivos: SistemaArchivos) -> None:
        self._sistema_archivos = sistema_archivos

    def ejecutar(self, plan: PlanGeneracion, ruta_destino: str) -> None:
        """Crea directorios necesarios y escribe todos los archivos del plan."""
        plan.comprobar_duplicados()
        for archivo in plan.archivos:
            ruta_absoluta = Path(ruta_destino) / archivo.ruta_relativa
            self._sistema_archivos.asegurar_directorio(str(ruta_absoluta.parent))
            self._sistema_archivos.escribir_texto_atomico(
                str(ruta_absoluta), archivo.contenido_texto
            )

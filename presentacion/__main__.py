"""Punto de entrada de consola para probar el flujo de generación base."""

from __future__ import annotations

import logging
from pathlib import Path

from aplicacion.casos_uso.crear_plan_proyecto_base import CrearPlanProyectoBase
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from dominio.modelos import EspecificacionProyecto
from infraestructura.logging_config import configurar_logging
from infraestructura.sistema_archivos_real import SistemaArchivosReal

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Configura infraestructura y ejecuta un flujo básico de generación."""
    configurar_logging("logs")
    LOGGER.info("Inicio de ejecución de la aplicación en modo mínimo.")

    especificacion = EspecificacionProyecto(
        nombre_proyecto="proyecto_demo",
        ruta_destino=str(Path("salida") / "proyecto_demo"),
        descripcion="Proyecto base de demostración generado por flujo mínimo.",
        version="0.1.0",
    )

    try:
        plan = CrearPlanProyectoBase().ejecutar(especificacion)
        EjecutarPlan(SistemaArchivosReal()).ejecutar(plan, especificacion.ruta_destino)
        LOGGER.info("Flujo finalizado correctamente para %s.", especificacion.nombre_proyecto)
    except Exception:
        LOGGER.exception("Fallo en la ejecución del flujo principal de la aplicación.")
        raise


if __name__ == "__main__":
    main()

"""Punto de entrada de consola para ejecutar generación por blueprints."""

from __future__ import annotations

import logging
from pathlib import Path

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generar_manifest import GenerarManifest
from dominio.modelos import EspecificacionProyecto
from infraestructura.calculadora_hash_real import CalculadoraHashReal
from infraestructura.logging_config import configurar_logging
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.sistema_archivos_real import SistemaArchivosReal

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Configura infraestructura y ejecuta el flujo completo."""
    configurar_logging("logs")
    LOGGER.info("Inicio de ejecución con sistema de blueprints.")

    especificacion = EspecificacionProyecto(
        nombre_proyecto="proyecto_demo",
        ruta_destino=str(Path("salida") / "proyecto_demo"),
        descripcion="Proyecto base de demostración generado por blueprints.",
        version="0.2.0",
    )
    nombres_blueprints = ["base_clean_arch"]

    try:
        repositorio = RepositorioBlueprintsEnDisco()
        plan = CrearPlanDesdeBlueprints(repositorio).ejecutar(
            especificacion, nombres_blueprints
        )
        generador_manifest = GenerarManifest(CalculadoraHashReal())
        EjecutarPlan(
            sistema_archivos=SistemaArchivosReal(),
            generador_manifest=generador_manifest,
        ).ejecutar(
            plan,
            especificacion.ruta_destino,
            opciones={"modo": "demo"},
            version_generador="0.2.0",
            blueprints_usados=["base_clean_arch@1.0.0"],
        )
        auditoria = AuditarProyectoGenerado().ejecutar(especificacion.ruta_destino)
        if not auditoria.valido:
            raise RuntimeError(f"Auditoría fallida: {auditoria.lista_errores}")
        LOGGER.info("Flujo finalizado correctamente para %s.", especificacion.nombre_proyecto)
    except Exception:
        LOGGER.exception("Fallo en la ejecución del flujo principal de la aplicación.")
        raise


if __name__ == "__main__":
    main()

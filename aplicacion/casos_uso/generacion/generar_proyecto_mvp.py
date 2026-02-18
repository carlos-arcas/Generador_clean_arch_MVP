"""Caso de uso MVP para generar proyecto funcional desde el wizard."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.puertos.sistema_archivos import SistemaArchivos
from dominio.modelos import EspecificacionProyecto

LOGGER = logging.getLogger(__name__)

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


@dataclass(frozen=True)
class GenerarProyectoMvpEntrada:
    """Entrada para ejecutar la generación MVP."""

    especificacion_proyecto: EspecificacionProyecto
    ruta_destino: str
    nombre_proyecto: str
    blueprints: list[str]


@dataclass(frozen=True)
class GenerarProyectoMvpSalida:
    """Resultado estructurado de la generación MVP."""

    ruta_generada: str
    archivos_generados: int
    valido: bool
    errores: list[str]


class GenerarProyectoMvp:
    """Orquesta la generación de proyecto reutilizando casos de uso existentes."""

    def __init__(
        self,
        crear_plan_desde_blueprints: CrearPlanDesdeBlueprints,
        ejecutar_plan: EjecutarPlan,
        sistema_archivos: SistemaArchivos,
    ) -> None:
        self._crear_plan = crear_plan_desde_blueprints
        self._ejecutar_plan = ejecutar_plan
        self._sistema_archivos = sistema_archivos

    def ejecutar(self, entrada: GenerarProyectoMvpEntrada) -> GenerarProyectoMvpSalida:
        """Genera el proyecto final en disco a partir de los blueprints MVP."""
        LOGGER.info(
            "Iniciando generación MVP para proyecto='%s' destino='%s' blueprints=%s",
            entrada.nombre_proyecto,
            entrada.ruta_destino,
            entrada.blueprints,
        )
        try:
            especificacion = entrada.especificacion_proyecto
            especificacion.nombre_proyecto = entrada.nombre_proyecto
            especificacion.ruta_destino = entrada.ruta_destino
            especificacion.validar()

            blueprints_normalizados = [
                blueprint.removesuffix("_v1") if blueprint.endswith("_v1") else blueprint
                for blueprint in entrada.blueprints
            ]
            LOGGER.debug("Blueprints normalizados para ejecución: %s", blueprints_normalizados)

            LOGGER.info("Etapa 1/3: asegurando estructura mínima de directorios")
            for directorio in DIRECTORIOS_BASE_MVP:
                self._sistema_archivos.asegurar_directorio(f"{entrada.ruta_destino}/{directorio}")

            LOGGER.info("Etapa 2/3: creando plan compuesto")
            plan = self._crear_plan.ejecutar(especificacion, blueprints_normalizados)

            LOGGER.info("Etapa 3/3: ejecutando plan en disco")
            self._ejecutar_plan.ejecutar(
                plan=plan,
                ruta_destino=entrada.ruta_destino,
                opciones={"origen": "wizard_mvp"},
                blueprints_usados=[f"{nombre}@1.0.0" for nombre in blueprints_normalizados],
                generar_manifest=True,
            )

            salida = GenerarProyectoMvpSalida(
                ruta_generada=entrada.ruta_destino,
                archivos_generados=len(plan.archivos),
                valido=True,
                errores=[],
            )
            LOGGER.info(
                "Generación MVP finalizada correctamente: ruta='%s' archivos=%s",
                salida.ruta_generada,
                salida.archivos_generados,
            )
            return salida
        except Exception as exc:
            LOGGER.exception("Error al generar proyecto MVP.")
            return GenerarProyectoMvpSalida(
                ruta_generada=entrada.ruta_destino,
                archivos_generados=0,
                valido=False,
                errores=[str(exc)],
            )

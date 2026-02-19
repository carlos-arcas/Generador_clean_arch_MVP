"""Paso de normalización inmutable de entrada para generación MVP."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from dominio.especificacion import EspecificacionProyecto

from aplicacion.casos_uso.generacion.pasos.errores_pipeline import ErrorNormalizacionEntradaGeneracion


@dataclass(frozen=True)
class DtoEntradaNormalizada:
    """Representa la entrada lista para ejecutar el pipeline."""

    especificacion_proyecto: EspecificacionProyecto
    ruta_proyecto: str
    nombre_proyecto: str
    blueprints: list[str]


class _EntradaGeneracion(Protocol):
    especificacion_proyecto: EspecificacionProyecto
    ruta_destino: str
    nombre_proyecto: str
    blueprints: list[str]


class NormalizadorEntradaGeneracion:
    """Construye una nueva especificación sin mutar la original."""

    def normalizar(self, entrada: _EntradaGeneracion, ruta_proyecto: Path) -> DtoEntradaNormalizada:
        try:
            blueprints_normalizados = [
                blueprint.removesuffix("_v1") if blueprint.endswith("_v1") else blueprint
                for blueprint in entrada.blueprints
            ]
            especificacion_original = entrada.especificacion_proyecto
            especificacion_normalizada = EspecificacionProyecto(
                nombre_proyecto=entrada.nombre_proyecto,
                ruta_destino=str(ruta_proyecto),
                descripcion=especificacion_original.descripcion,
                version=especificacion_original.version,
                clases=especificacion_original.clases.copy(),
            )
            especificacion_normalizada.validar()
            return DtoEntradaNormalizada(
                especificacion_proyecto=especificacion_normalizada,
                ruta_proyecto=str(ruta_proyecto),
                nombre_proyecto=entrada.nombre_proyecto,
                blueprints=blueprints_normalizados,
            )
        except (TypeError, ValueError) as exc:
            raise ErrorNormalizacionEntradaGeneracion(
                "No se pudo normalizar la entrada de generación."
            ) from exc

"""Paso de validación de entrada para generación MVP."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from aplicacion.casos_uso.generacion.pasos.errores_pipeline import ErrorValidacionEntradaGeneracion
from dominio.especificacion import EspecificacionProyecto
from dominio.excepciones.proyecto_ya_existe_error import ProyectoYaExisteError


class _EntradaGeneracion(Protocol):
    especificacion_proyecto: EspecificacionProyecto
    ruta_destino: str
    nombre_proyecto: str


class ValidadorEntradaGeneracion:
    """Valida contratos básicos y estado de la ruta de salida."""

    def validar(self, entrada: _EntradaGeneracion) -> Path:
        if entrada is None:
            raise ErrorValidacionEntradaGeneracion("La entrada no puede ser nula.")
        if not entrada.nombre_proyecto.strip():
            raise ErrorValidacionEntradaGeneracion("El nombre del proyecto es obligatorio.")
        if not entrada.ruta_destino.strip():
            raise ErrorValidacionEntradaGeneracion("La ruta destino es obligatoria.")
        if entrada.especificacion_proyecto is None:
            raise ErrorValidacionEntradaGeneracion("La especificación del proyecto es obligatoria.")

        ruta_proyecto = Path(entrada.ruta_destino) / entrada.nombre_proyecto
        if ruta_proyecto.exists() and any(ruta_proyecto.iterdir()):
            raise ProyectoYaExisteError(
                f"La carpeta destino '{ruta_proyecto}' ya existe y no está vacía."
            )
        return ruta_proyecto

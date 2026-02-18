"""Orquestación del flujo de finalización del wizard."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable

from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvpEntrada
from presentacion.wizard.dtos import DatosWizardProyecto

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DtoEntradaFinalizacionWizard:
    """Entrada para finalizar el wizard sin dependencias de Qt."""

    datos_wizard: DatosWizardProyecto
    blueprints: list[str]


@dataclass(frozen=True)
class DtoResultadoFinalizacionWizard:
    """Resultado tipado del flujo de finalización."""

    exito: bool
    mensaje_usuario: str
    detalles: dict[str, Any] | None = None


class ServicioCredencialesWizardNulo:
    """Stub por defecto para el guardado de credenciales del wizard."""

    def ejecutar_desde_datos(
        self,
        identificador: str,
        usuario: str,
        secreto: str,
        tipo: str,
    ) -> None:
        del identificador, usuario, secreto, tipo


class OrquestadorFinalizacionWizard:
    """Coordina validación, credenciales y lanzamiento de generación."""

    def __init__(
        self,
        validador_final: Callable[[Any], Any],
        lanzador_generacion: Callable[[GenerarProyectoMvpEntrada], None],
        servicio_credenciales: Any | None = None,
        servicio_presets: Any | None = None,
    ) -> None:
        self._validador_final = validador_final
        self._lanzador_generacion = lanzador_generacion
        self._servicio_credenciales = servicio_credenciales or ServicioCredencialesWizardNulo()
        self._servicio_presets = servicio_presets

    def finalizar(self, dto: DtoEntradaFinalizacionWizard) -> DtoResultadoFinalizacionWizard:
        detalles: dict[str, Any] = {}

        if dto.datos_wizard.guardar_credencial and dto.datos_wizard.usuario_credencial and dto.datos_wizard.secreto_credencial:
            identificador = (
                f"generador:{dto.datos_wizard.nombre}:{dto.datos_wizard.persistencia.lower()}"
            )
            try:
                self._servicio_credenciales.ejecutar_desde_datos(
                    identificador=identificador,
                    usuario=dto.datos_wizard.usuario_credencial,
                    secreto=dto.datos_wizard.secreto_credencial,
                    tipo=dto.datos_wizard.persistencia,
                )
                detalles["credencial_guardada"] = True
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning(
                    "No se pudo persistir credencial en almacenamiento seguro. Se continuará solo en memoria. %s",
                    exc,
                )
                detalles["advertencia_credenciales"] = (
                    "No se pudo guardar la credencial en el sistema seguro. "
                    "Se usará únicamente en memoria durante esta ejecución."
                )

        if self._servicio_presets is not None:
            detalles["presets_disponibles"] = True

        try:
            especificacion = self._validador_final(dto.datos_wizard.proyecto)
        except Exception as exc:  # noqa: BLE001
            return DtoResultadoFinalizacionWizard(
                exito=False,
                mensaje_usuario=f"Error de validación: {exc}",
                detalles=detalles or None,
            )

        entrada_generacion = GenerarProyectoMvpEntrada(
            especificacion_proyecto=especificacion,
            ruta_destino=dto.datos_wizard.ruta,
            nombre_proyecto=dto.datos_wizard.nombre,
            blueprints=dto.blueprints,
        )

        try:
            self._lanzador_generacion(entrada_generacion)
        except Exception as exc:  # noqa: BLE001
            return DtoResultadoFinalizacionWizard(
                exito=False,
                mensaje_usuario=f"Error al iniciar generación: {exc}",
                detalles=detalles or None,
            )

        detalles["generacion_iniciada"] = True
        return DtoResultadoFinalizacionWizard(
            exito=True,
            mensaje_usuario="Generación iniciada.",
            detalles=detalles,
        )

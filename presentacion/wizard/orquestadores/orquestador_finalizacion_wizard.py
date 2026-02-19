"""Orquestación del flujo de finalización del wizard."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable

from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvpEntrada
from aplicacion.errores import (
    ErrorAplicacion,
    ErrorAuditoria,
    ErrorGeneracionProyecto,
    ErrorInfraestructura,
    ErrorValidacionEntrada,
)
from presentacion.wizard.dtos import DatosWizardProyecto

LOGGER = logging.getLogger(__name__)


class _ErrorInfraestructuraValidacionWizard(Exception):
    """Error técnico al validar datos finales del wizard."""


class _ErrorInfraestructuraGeneracionWizard(Exception):
    """Error técnico al iniciar generación desde el wizard."""


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
        detalles = self._crear_detalles_base()
        try:
            self._validar_entrada(dto)
            self._persistir_credenciales(dto, detalles)
            entrada_generacion = self._preparar_dto_generacion(dto)
            self._ejecutar_generacion(entrada_generacion)
            return self._construir_resultado_exitoso(detalles)
        except (
            ErrorAplicacion,
            ErrorValidacionEntrada,
            ErrorGeneracionProyecto,
            ErrorAuditoria,
            ValueError,
            TypeError,
        ) as error:
            return self._construir_resultado_error(error, detalles)
        except (
            _ErrorInfraestructuraValidacionWizard,
            _ErrorInfraestructuraGeneracionWizard,
        ) as error:
            return self._construir_resultado_error(error, detalles)

    def _crear_detalles_base(self) -> dict[str, Any]:
        detalles: dict[str, Any] = {}
        if self._servicio_presets is not None:
            detalles["presets_disponibles"] = True
        return detalles

    def _validar_entrada(self, dto: DtoEntradaFinalizacionWizard) -> None:
        if dto.datos_wizard is None:
            raise ValueError("Los datos del wizard son obligatorios.")
        if dto.datos_wizard.proyecto is None:
            raise ValueError("El proyecto a validar es obligatorio.")

    def _preparar_dto_generacion(
        self,
        dto: DtoEntradaFinalizacionWizard,
    ) -> GenerarProyectoMvpEntrada:
        try:
            especificacion = self._validador_final(dto.datos_wizard.proyecto)
        except (ErrorInfraestructura, OSError, PermissionError, IOError) as error:
            raise _ErrorInfraestructuraValidacionWizard() from error
        return GenerarProyectoMvpEntrada(
            especificacion_proyecto=especificacion,
            ruta_destino=dto.datos_wizard.ruta,
            nombre_proyecto=dto.datos_wizard.nombre,
            blueprints=dto.blueprints,
        )

    def _persistir_credenciales(
        self,
        dto: DtoEntradaFinalizacionWizard,
        detalles: dict[str, Any],
    ) -> None:
        if not self._debe_guardar_credenciales(dto):
            return
        identificador = f"generador:{dto.datos_wizard.nombre}:{dto.datos_wizard.persistencia.lower()}"
        try:
            self._servicio_credenciales.ejecutar_desde_datos(
                identificador=identificador,
                usuario=dto.datos_wizard.usuario_credencial,
                secreto=dto.datos_wizard.secreto_credencial,
                tipo=dto.datos_wizard.persistencia,
            )
            detalles["credencial_guardada"] = True
        except (ErrorInfraestructura, OSError, PermissionError, IOError, ValueError) as error:
            LOGGER.warning(
                "No se pudo persistir credencial en almacenamiento seguro. Se continuará solo en memoria. %s",
                error,
                exc_info=True,
            )
            detalles["advertencia_credenciales"] = (
                "No se pudo guardar la credencial en el sistema seguro. "
                "Se usará únicamente en memoria durante esta ejecución."
            )

    def _debe_guardar_credenciales(self, dto: DtoEntradaFinalizacionWizard) -> bool:
        return (
            dto.datos_wizard.guardar_credencial
            and bool(dto.datos_wizard.usuario_credencial)
            and bool(dto.datos_wizard.secreto_credencial)
        )

    def _ejecutar_generacion(self, entrada_generacion: GenerarProyectoMvpEntrada) -> None:
        try:
            self._lanzador_generacion(entrada_generacion)
        except (ErrorInfraestructura, OSError, PermissionError, IOError) as error:
            raise _ErrorInfraestructuraGeneracionWizard() from error

    def _construir_resultado_exitoso(
        self,
        detalles: dict[str, Any],
    ) -> DtoResultadoFinalizacionWizard:
        detalles["generacion_iniciada"] = True
        return DtoResultadoFinalizacionWizard(
            exito=True,
            mensaje_usuario="Generación iniciada.",
            detalles=detalles,
        )

    def _construir_resultado_error(
        self,
        error: Exception,
        detalles: dict[str, Any],
    ) -> DtoResultadoFinalizacionWizard:
        mensaje_usuario = self._mapear_mensaje_error(error)
        return DtoResultadoFinalizacionWizard(
            exito=False,
            mensaje_usuario=mensaje_usuario,
            detalles=detalles or None,
        )

    def _mapear_mensaje_error(self, error: Exception) -> str:
        if isinstance(error, (ErrorValidacionEntrada, ValueError, TypeError)):
            return f"Error de validación: {error}"
        if isinstance(error, (ErrorGeneracionProyecto, ErrorAuditoria)):
            return f"Error al iniciar generación: {error}"
        if isinstance(error, _ErrorInfraestructuraValidacionWizard):
            LOGGER.error("Error técnico durante validación final del wizard.", exc_info=True)
            return "Error técnico durante la validación final."
        if isinstance(error, _ErrorInfraestructuraGeneracionWizard):
            LOGGER.error("Error técnico al iniciar la generación del proyecto.", exc_info=True)
            return "Error técnico al iniciar generación."
        if isinstance(error, ErrorAplicacion):
            return f"Error al iniciar generación: {error}"
        LOGGER.error("Error técnico no esperado durante la finalización del wizard.", exc_info=True)
        return "Error técnico al iniciar generación."

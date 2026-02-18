"""Controlador de orquestación para el wizard."""

from __future__ import annotations

from aplicacion.dtos.proyecto import DtoProyectoEntrada
from presentacion.wizard.dtos import DatosWizardProyecto
from presentacion.wizard.estado.estado_wizard import EstadoWizardProyecto


class ControladorWizardProyecto:
    """Construye DTOs de presentación a partir del estado del wizard."""

    def construir_dto_desde_estado(self, estado: EstadoWizardProyecto) -> DatosWizardProyecto:
        proyecto = DtoProyectoEntrada(
            nombre_proyecto=estado.nombre,
            ruta_destino=estado.ruta,
            descripcion=estado.descripcion,
            version=estado.version,
            clases=estado.clases,
        )
        return DatosWizardProyecto(
            nombre=proyecto.nombre_proyecto,
            ruta=proyecto.ruta_destino,
            descripcion=proyecto.descripcion,
            version=proyecto.version,
            proyecto=proyecto,
            persistencia=estado.persistencia,
            usuario_credencial=estado.usuario_credencial,
            secreto_credencial=estado.secreto_credencial,
            guardar_credencial=estado.guardar_credencial,
        )

"""Controlador de orquestación para el wizard de generación."""

from __future__ import annotations

import logging

from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvpEntrada
from dominio.preset.preset_proyecto import PresetProyecto
from dominio.seguridad import Credencial
from presentacion.wizard.dtos import DatosWizardProyecto

LOGGER = logging.getLogger(__name__)


class ControladorWizardProyecto:
    """Orquesta estado + casos de uso del wizard sin depender de widgets concretos."""

    def construir_dto(self, vista: object) -> DatosWizardProyecto:
        self.sincronizar_especificacion(vista)
        return DatosWizardProyecto(
            nombre=vista.pagina_datos.campo_nombre.text().strip(),
            ruta=vista.pagina_datos.campo_ruta.text().strip(),
            descripcion=vista.pagina_datos.campo_descripcion.text().strip(),
            version=vista.pagina_datos.campo_version.text().strip(),
            especificacion_proyecto=vista.estado.especificacion_proyecto,
            persistencia=vista.pagina_persistencia.persistencia_seleccionada(),
            usuario_credencial=vista.pagina_persistencia.usuario_credencial(),
            secreto_credencial=vista.pagina_persistencia.secreto_credencial(),
            guardar_credencial=vista.pagina_persistencia.guardar_credencial_segura(),
        )

    def sincronizar_especificacion(self, vista: object) -> None:
        vista.estado.especificacion_proyecto.nombre_proyecto = vista.pagina_datos.campo_nombre.text().strip()
        vista.estado.especificacion_proyecto.ruta_destino = vista.pagina_datos.campo_ruta.text().strip()
        vista.estado.especificacion_proyecto.descripcion = vista.pagina_datos.campo_descripcion.text().strip()
        vista.estado.especificacion_proyecto.version = vista.pagina_datos.campo_version.text().strip()

    def crear_credencial(self, dto: DatosWizardProyecto) -> Credencial:
        identificador = f"generador:{dto.nombre}:{dto.persistencia.lower()}"
        return Credencial(
            identificador=identificador,
            usuario=dto.usuario_credencial,
            secreto=dto.secreto_credencial,
            tipo=dto.persistencia,
        )

    def crear_preset(self, vista: object, nombre: str) -> PresetProyecto:
        self.sincronizar_especificacion(vista)
        return PresetProyecto(
            nombre=nombre,
            especificacion=vista.estado.especificacion_proyecto,
            blueprints=vista.blueprints_seleccionados(),
            metadata={"persistencia": vista.pagina_persistencia.persistencia_seleccionada()},
        )

    def crear_entrada_generacion(self, dto: DatosWizardProyecto, blueprints: list[str]) -> GenerarProyectoMvpEntrada:
        return GenerarProyectoMvpEntrada(
            especificacion_proyecto=dto.especificacion_proyecto,
            ruta_destino=dto.ruta,
            nombre_proyecto=dto.nombre,
            blueprints=blueprints,
        )

"""Wizard principal para configurar generación de proyectos (MVP)."""

from __future__ import annotations

from dataclasses import asdict
import logging

from PySide6.QtWidgets import QMessageBox, QWizard

from dominio.modelos import EspecificacionProyecto
from presentacion.wizard.dtos import DatosWizardProyecto
from presentacion.wizard.paginas.pagina_clases import PaginaClases
from presentacion.wizard.paginas.pagina_datos_proyecto import PaginaDatosProyecto
from presentacion.wizard.paginas.pagina_persistencia import PaginaPersistencia
from presentacion.wizard.paginas.pagina_resumen import PaginaResumen

LOGGER = logging.getLogger(__name__)


class ControladorWizardProyecto:
    """Orquesta la recopilación de datos del wizard para siguientes pasos."""

    def construir_dto(self, wizard: "WizardGeneradorProyectos") -> DatosWizardProyecto:
        wizard.especificacion_proyecto.nombre_proyecto = wizard.pagina_datos.campo_nombre.text().strip()
        wizard.especificacion_proyecto.ruta_destino = wizard.pagina_datos.campo_ruta.text().strip()
        wizard.especificacion_proyecto.descripcion = wizard.pagina_datos.campo_descripcion.text().strip()
        wizard.especificacion_proyecto.version = wizard.pagina_datos.campo_version.text().strip()
        return DatosWizardProyecto(
            nombre=wizard.pagina_datos.campo_nombre.text().strip(),
            ruta=wizard.pagina_datos.campo_ruta.text().strip(),
            descripcion=wizard.pagina_datos.campo_descripcion.text().strip(),
            version=wizard.pagina_datos.campo_version.text().strip(),
            especificacion_proyecto=wizard.especificacion_proyecto,
            persistencia=wizard.pagina_persistencia.persistencia_seleccionada(),
        )


class WizardGeneradorProyectos(QWizard):
    """Wizard de 4 pasos para preparar configuración de generación."""

    def __init__(self, controlador: ControladorWizardProyecto | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Generador Base Proyectos")

        self._controlador = controlador or ControladorWizardProyecto()
        self.especificacion_proyecto = EspecificacionProyecto(nombre_proyecto="", ruta_destino="")

        self.pagina_datos = PaginaDatosProyecto()
        self.pagina_clases = PaginaClases()
        self.pagina_persistencia = PaginaPersistencia()
        self.pagina_resumen = PaginaResumen()

        self.addPage(self.pagina_datos)
        self.addPage(self.pagina_clases)
        self.addPage(self.pagina_persistencia)
        self.addPage(self.pagina_resumen)

        self.button(QWizard.FinishButton).clicked.connect(self._al_finalizar)

    def _al_finalizar(self) -> None:
        dto = self._controlador.construir_dto(self)
        LOGGER.info("Configuración wizard lista: %s", asdict(dto))
        QMessageBox.information(
            self,
            "Configuración lista",
            "Configuración lista. En el siguiente paso se implementará la generación",
        )

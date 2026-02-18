"""Wizard principal para configurar generación de proyectos (MVP)."""

from __future__ import annotations

import logging

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QInputDialog,
    QLabel,
    QMessageBox,
    QProgressBar,
    QVBoxLayout,
    QWizard,
)

from aplicacion.casos_uso.generacion.generar_proyecto_mvp import (
    GenerarProyectoMvp,
    GenerarProyectoMvpEntrada,
    GenerarProyectoMvpSalida,
)
from aplicacion.casos_uso.presets import CargarPresetProyecto, GuardarPresetProyecto
from aplicacion.casos_uso.seguridad import GuardarCredencial
from dominio.modelos import EspecificacionProyecto
from dominio.seguridad import Credencial
from dominio.preset.preset_proyecto import PresetProyecto
from presentacion.wizard.dtos import DatosWizardProyecto
from presentacion.wizard.paginas.pagina_clases import PaginaClases
from presentacion.wizard.paginas.pagina_datos_proyecto import PaginaDatosProyecto
from presentacion.wizard.paginas.pagina_persistencia import PaginaPersistencia
from presentacion.wizard.paginas.pagina_resumen import PaginaResumen
from presentacion.wizard.trabajadores.trabajador_generacion import TrabajadorGeneracionMvp

LOGGER = logging.getLogger(__name__)

BLUEPRINTS_MVP = ["base_clean_arch", "crud_json"]


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
            usuario_credencial=wizard.pagina_persistencia.usuario_credencial(),
            secreto_credencial=wizard.pagina_persistencia.secreto_credencial(),
            guardar_credencial=wizard.pagina_persistencia.guardar_credencial_segura(),
        )


class WizardGeneradorProyectos(QWizard):
    """Wizard de 4 pasos para preparar configuración de generación."""

    def __init__(
        self,
        controlador: ControladorWizardProyecto | None = None,
        generar_proyecto: GenerarProyectoMvp | None = None,
        generador_mvp: GenerarProyectoMvp | None = None,
        guardar_preset: GuardarPresetProyecto | None = None,
        cargar_preset: CargarPresetProyecto | None = None,
        guardar_credencial: GuardarCredencial | None = None,
        catalogo_blueprints: list[tuple[str, str, str]] | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Generador Base Proyectos")

        if generar_proyecto is None and generador_mvp is not None:
            generar_proyecto = generador_mvp

        if (
            generar_proyecto is None
            or guardar_preset is None
            or cargar_preset is None
            or guardar_credencial is None
            or catalogo_blueprints is None
        ):
            from bootstrap.composition_root import crear_contenedor

            contenedor = crear_contenedor()
            generar_proyecto = generar_proyecto or contenedor.generar_proyecto_mvp
            guardar_preset = guardar_preset or contenedor.guardar_preset_proyecto
            cargar_preset = cargar_preset or contenedor.cargar_preset_proyecto
            guardar_credencial = guardar_credencial or contenedor.guardar_credencial
            catalogo_blueprints = catalogo_blueprints or contenedor.catalogo_blueprints

        self._controlador = controlador or ControladorWizardProyecto()
        self._pool = QThreadPool.globalInstance()
        self._trabajador_activo: TrabajadorGeneracionMvp | None = None
        self._generador_mvp = generar_proyecto
        self._guardar_preset = guardar_preset
        self._cargar_preset = cargar_preset
        self._guardar_credencial = guardar_credencial
        self._catalogo_blueprints = catalogo_blueprints

        self.especificacion_proyecto = EspecificacionProyecto(nombre_proyecto="", ruta_destino="")

        self.pagina_datos = PaginaDatosProyecto()
        self.pagina_clases = PaginaClases()
        self.pagina_persistencia = PaginaPersistencia()
        self.pagina_resumen = PaginaResumen()

        self.addPage(self.pagina_datos)
        self.addPage(self.pagina_clases)
        self.addPage(self.pagina_persistencia)
        self.addPage(self.pagina_resumen)

        self._etiqueta_estado = QLabel("")
        self._barra_progreso = QProgressBar()
        self._barra_progreso.setRange(0, 0)
        self._barra_progreso.hide()

        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.addWidget(self._etiqueta_estado)
            layout.addWidget(self._barra_progreso)

        self.pagina_datos.boton_guardar_preset.clicked.connect(self._guardar_preset_desde_ui)
        self.pagina_datos.boton_cargar_preset.clicked.connect(self._cargar_preset_desde_ui)
        self.button(QWizard.FinishButton).clicked.connect(self._al_finalizar)

        self.pagina_persistencia.establecer_blueprints_disponibles(
            self._catalogo_blueprints,
            BLUEPRINTS_MVP,
        )

    def _al_finalizar(self) -> None:
        dto = self._controlador.construir_dto(self)
        LOGGER.info(
            "Configuración wizard lista: nombre=%s ruta=%s persistencia=%s usuario_configurado=%s guardar_credencial=%s",
            dto.nombre,
            dto.ruta,
            dto.persistencia,
            bool(dto.usuario_credencial),
            dto.guardar_credencial,
        )

        if dto.guardar_credencial and dto.usuario_credencial and dto.secreto_credencial:
            identificador = f"generador:{dto.nombre}:{dto.persistencia.lower()}"
            try:
                self._guardar_credencial.ejecutar(
                    Credencial(
                        identificador=identificador,
                        usuario=dto.usuario_credencial,
                        secreto=dto.secreto_credencial,
                        tipo=dto.persistencia,
                    )
                )
                LOGGER.info("Credencial almacenada de forma segura para identificador=%s", identificador)
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning(
                    "No se pudo persistir credencial en almacenamiento seguro. Se continuará solo en memoria. %s",
                    exc,
                )
                QMessageBox.warning(
                    self,
                    "Credenciales",
                    "No se pudo guardar la credencial en el sistema seguro. Se usará únicamente en memoria durante esta ejecución.",
                )

        entrada = GenerarProyectoMvpEntrada(
            especificacion_proyecto=dto.especificacion_proyecto,
            ruta_destino=dto.ruta,
            nombre_proyecto=dto.nombre,
            blueprints=self._blueprints_seleccionados(),
        )
        self._cambiar_estado_generando(True, "Generando...")

        trabajador = TrabajadorGeneracionMvp(caso_uso=self._generador_mvp, entrada=entrada)
        trabajador.senales.progreso.connect(self._actualizar_estado)
        trabajador.senales.exito.connect(self._on_generacion_exitosa)
        trabajador.senales.error.connect(self._on_generacion_error)
        self._trabajador_activo = trabajador
        self._pool.start(trabajador)

    def _guardar_preset_desde_ui(self) -> None:
        nombre, aceptado = QInputDialog.getText(self, "Guardar preset", "Nombre del preset")
        if not aceptado:
            return

        nombre = nombre.strip()
        if not nombre:
            QMessageBox.warning(self, "Guardar preset", "Debes indicar un nombre de preset.")
            return

        try:
            self._sincronizar_especificacion_desde_campos()
            preset = PresetProyecto(
                nombre=nombre,
                especificacion=self.especificacion_proyecto,
                blueprints=self._blueprints_seleccionados(),
                metadata={"persistencia": self.pagina_persistencia.persistencia_seleccionada()},
            )
            ruta = self._guardar_preset.ejecutar(preset)
            QMessageBox.information(self, "Guardar preset", f"Preset guardado en: {ruta}")
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("No se pudo guardar preset: %s", exc)
            QMessageBox.critical(self, "Guardar preset", str(exc))

    def _cargar_preset_desde_ui(self) -> None:
        try:
            nombres = self._cargar_preset._almacen.listar()  # noqa: SLF001
            if not nombres:
                QMessageBox.information(self, "Cargar preset", "No hay presets disponibles.")
                return
            nombre, aceptado = QInputDialog.getItem(
                self,
                "Cargar preset",
                "Selecciona un preset",
                nombres,
                editable=False,
            )
            if not aceptado:
                return
            preset = self._cargar_preset.ejecutar(nombre)
            self.aplicar_preset(preset)
            QMessageBox.information(self, "Cargar preset", f"Preset '{nombre}' cargado.")
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("No se pudo cargar preset: %s", exc)
            QMessageBox.critical(self, "Cargar preset", str(exc))

    def aplicar_preset(self, preset: PresetProyecto) -> None:
        self.especificacion_proyecto = preset.especificacion
        self.pagina_datos.campo_nombre.setText(preset.especificacion.nombre_proyecto)
        self.pagina_datos.campo_ruta.setText(preset.especificacion.ruta_destino)
        self.pagina_datos.campo_descripcion.setText(preset.especificacion.descripcion or "")
        self.pagina_datos.campo_version.setText(preset.especificacion.version)
        persistencia = str(preset.metadata.get("persistencia", "JSON"))
        self.pagina_persistencia.establecer_persistencia(persistencia)
        self.pagina_clases.establecer_desde_especificacion(self.especificacion_proyecto)
        self.pagina_persistencia.establecer_blueprints_disponibles(
            self._catalogo_blueprints,
            preset.blueprints,
        )
        self.pagina_resumen.initializePage()

    def _blueprints_seleccionados(self) -> list[str]:
        seleccionados = self.pagina_persistencia.blueprints_seleccionados()
        if seleccionados:
            return seleccionados
        return BLUEPRINTS_MVP

    def _sincronizar_especificacion_desde_campos(self) -> None:
        self.especificacion_proyecto.nombre_proyecto = self.pagina_datos.campo_nombre.text().strip()
        self.especificacion_proyecto.ruta_destino = self.pagina_datos.campo_ruta.text().strip()
        self.especificacion_proyecto.descripcion = self.pagina_datos.campo_descripcion.text().strip()
        self.especificacion_proyecto.version = self.pagina_datos.campo_version.text().strip()

    def _actualizar_estado(self, texto: str) -> None:
        self._etiqueta_estado.setText(texto)

    def _cambiar_estado_generando(self, activo: bool, texto: str = "") -> None:
        self.button(QWizard.BackButton).setEnabled(not activo)
        self.button(QWizard.NextButton).setEnabled(not activo)
        self.button(QWizard.FinishButton).setEnabled(not activo)
        self._etiqueta_estado.setText(texto)
        self._barra_progreso.setVisible(activo)

    def _on_generacion_exitosa(self, salida: GenerarProyectoMvpSalida) -> None:
        self._cambiar_estado_generando(False, "")
        LOGGER.info(
            "Generación completada en wizard: ruta=%s archivos=%s valido=%s errores=%s warnings=%s",
            salida.ruta_generada,
            salida.archivos_generados,
            salida.valido,
            len(salida.errores),
            len(salida.warnings),
        )
        mensaje = (
            "Proyecto generado correctamente.\n"
            "Auditoría:\n"
            f"   Errores: {len(salida.errores)}\n"
            f"   Warnings: {len(salida.warnings)}"
        )
        if salida.valido:
            QMessageBox.information(self, "Generación completada", mensaje)
            return

        detalle = "\n".join(salida.errores) if salida.errores else "Sin detalles adicionales"
        QMessageBox.warning(
            self,
            "Generación completada con observaciones",
            f"{mensaje}\n\nSe detectaron errores críticos de auditoría:\n{detalle}",
        )

    def _on_generacion_error(self, mensaje: str, detalle: str) -> None:
        self._cambiar_estado_generando(False, "")
        LOGGER.error("Falló la generación desde wizard: %s | detalle=%s", mensaje, detalle)
        QMessageBox.critical(
            self,
            "Error de generación",
            f"{mensaje}\n\nDetalle:\n{detalle}",
        )

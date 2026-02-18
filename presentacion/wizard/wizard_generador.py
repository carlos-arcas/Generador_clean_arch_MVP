"""Wizard principal para configurar generación de proyectos (MVP)."""

from __future__ import annotations

from dataclasses import asdict
import logging
from pathlib import Path
import traceback

from PySide6.QtCore import QThreadPool, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QInputDialog,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWizard,
)

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import (
    GenerarProyectoMvp,
    GenerarProyectoMvpEntrada,
    GenerarProyectoMvpSalida,
)
from aplicacion.casos_uso.generar_manifest import GenerarManifest
from aplicacion.casos_uso.presets import CargarPresetProyecto, GuardarPresetProyecto
from dominio.modelos import EspecificacionProyecto
from dominio.preset.preset_proyecto import PresetProyecto
from infraestructura.calculadora_hash_real import CalculadoraHashReal
from infraestructura.plugins.descubridor_plugins import DescubridorPlugins
from infraestructura.presets.repositorio_presets_json import RepositorioPresetsJson
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.sistema_archivos_real import SistemaArchivosReal
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
        )


class WizardGeneradorProyectos(QWizard):
    """Wizard de 4 pasos para preparar configuración de generación."""

    def __init__(
        self,
        controlador: ControladorWizardProyecto | None = None,
        generador_mvp: GenerarProyectoMvp | None = None,
        guardar_preset: GuardarPresetProyecto | None = None,
        cargar_preset: CargarPresetProyecto | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Generador Base Proyectos")

        self._controlador = controlador or ControladorWizardProyecto()
        self._pool = QThreadPool.globalInstance()
        self._trabajador_activo: TrabajadorGeneracionMvp | None = None
        self._repositorio_blueprints = RepositorioBlueprintsEnDisco("blueprints")
        self._descubridor_plugins = DescubridorPlugins("plugins")

        if generador_mvp is None:
            crear_plan = CrearPlanDesdeBlueprints(
                self._repositorio_blueprints,
                descubridor_plugins=self._descubridor_plugins,
            )
            generar_manifest = GenerarManifest(CalculadoraHashReal())
            ejecutar_plan = EjecutarPlan(SistemaArchivosReal(), generar_manifest)
            sistema_archivos = SistemaArchivosReal()
            self._generador_mvp = GenerarProyectoMvp(crear_plan, ejecutar_plan, sistema_archivos)
        else:
            self._generador_mvp = generador_mvp

        self._guardar_preset = guardar_preset or GuardarPresetProyecto(RepositorioPresetsJson())
        self._cargar_preset = cargar_preset or CargarPresetProyecto(RepositorioPresetsJson())

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
        self._boton_cancelar_generacion = QPushButton("Cancelar generación")
        self._boton_cancelar_generacion.hide()
        self._boton_cancelar_generacion.clicked.connect(self._cancelar_generacion)

        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.addWidget(self._etiqueta_estado)
            layout.addWidget(self._barra_progreso)
            layout.addWidget(self._boton_cancelar_generacion)

        self.pagina_datos.boton_guardar_preset.clicked.connect(self._guardar_preset_desde_ui)
        self.pagina_datos.boton_cargar_preset.clicked.connect(self._cargar_preset_desde_ui)
        self.button(QWizard.FinishButton).clicked.connect(self._al_finalizar)

        self._cargar_catalogo_blueprints()

    def _al_finalizar(self) -> None:
        try:
            dto = self._controlador.construir_dto(self)
            LOGGER.info("Configuración wizard lista: %s", asdict(dto))

            entrada = GenerarProyectoMvpEntrada(
                especificacion_proyecto=dto.especificacion_proyecto,
                ruta_destino=dto.ruta,
                nombre_proyecto=dto.nombre,
                blueprints=self._blueprints_seleccionados(),
            )
            self._cambiar_estado_generando(True, "Validando ruta destino...")

            trabajador = TrabajadorGeneracionMvp(caso_uso=self._generador_mvp, entrada=entrada)
            trabajador.senales.progreso.connect(self._actualizar_estado)
            trabajador.senales.exito.connect(self._on_generacion_exitosa)
            trabajador.senales.cancelado.connect(self._on_generacion_cancelada)
            trabajador.senales.error.connect(self._on_generacion_error)
            self._trabajador_activo = trabajador
            self._pool.start(trabajador)
        except Exception as exc:  # noqa: BLE001
            self._manejar_excepcion_visual(exc, "No se pudo iniciar la generación.")

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

    def _cargar_catalogo_blueprints(self) -> None:
        internos = [
            (blueprint.nombre(), blueprint.version(), "Blueprint interno")
            for blueprint in self._repositorio_blueprints.listar_blueprints()
        ]
        externos = [
            (plugin.nombre, plugin.version, plugin.descripcion)
            for plugin in self._descubridor_plugins.listar_plugins()
        ]
        catalogo_unico: dict[str, tuple[str, str, str]] = {
            nombre: (nombre, version, descripcion)
            for nombre, version, descripcion in [*internos, *externos]
        }
        self._catalogo_blueprints = sorted(catalogo_unico.values(), key=lambda item: item[0])
        self.pagina_persistencia.establecer_blueprints_disponibles(
            self._catalogo_blueprints,
            BLUEPRINTS_MVP,
        )

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
        self._boton_cancelar_generacion.setVisible(activo)
        self._boton_cancelar_generacion.setEnabled(activo)

    def _cancelar_generacion(self) -> None:
        if self._trabajador_activo is None:
            return
        self._trabajador_activo.cancelar()
        self._boton_cancelar_generacion.setEnabled(False)
        self._actualizar_estado("Cancelando generación...")

    def _on_generacion_exitosa(self, salida: GenerarProyectoMvpSalida) -> None:
        self._trabajador_activo = None
        self._cambiar_estado_generando(False, "")
        LOGGER.info(
            "Generación completada en wizard: ruta=%s archivos=%s valido=%s errores=%s warnings=%s",
            salida.ruta_generada,
            salida.archivos_generados,
            salida.valido,
            len(salida.errores),
            len(salida.warnings),
        )

        if not salida.valido:
            self._mostrar_error_generacion()
            return

        self._mostrar_dialogo_exito(salida)

    def _on_generacion_cancelada(self, mensaje: str) -> None:
        self._trabajador_activo = None
        self._cambiar_estado_generando(False, mensaje)
        QMessageBox.information(self, "Generación cancelada", mensaje)

    def _on_generacion_error(self, mensaje: str, detalle: str) -> None:
        self._trabajador_activo = None
        self._cambiar_estado_generando(False, "")
        LOGGER.error("Falló la generación desde wizard: %s | detalle=%s", mensaje, detalle)
        self._mostrar_error_generacion()

    def _mostrar_dialogo_exito(self, salida: GenerarProyectoMvpSalida) -> None:
        mensaje = QMessageBox(self)
        mensaje.setIcon(QMessageBox.Information)
        mensaje.setWindowTitle("Generación completada")
        mensaje.setText("Proyecto generado correctamente.")
        mensaje.setInformativeText(
            "\n".join(
                [
                    f"Ruta generada: {salida.ruta_generada}",
                    f"Número de archivos: {salida.archivos_generados}",
                    "Resultado auditoría:",
                    f"Errores: {len(salida.errores)}",
                    f"Warnings: {len(salida.warnings)}",
                ]
            )
        )
        abrir_btn = mensaje.addButton("Abrir carpeta del proyecto", QMessageBox.ActionRole)
        mensaje.addButton(QMessageBox.Ok)
        mensaje.exec()
        if mensaje.clickedButton() is abrir_btn:
            self._abrir_carpeta(salida.ruta_generada)

    def _mostrar_error_generacion(self) -> None:
        mensaje = QMessageBox(self)
        mensaje.setIcon(QMessageBox.Critical)
        mensaje.setWindowTitle("Error de generación")
        mensaje.setText("La generación falló.")
        mensaje.setInformativeText("Revisa logs en carpeta logs/")
        abrir_logs_btn = mensaje.addButton("Abrir carpeta logs", QMessageBox.ActionRole)
        mensaje.addButton(QMessageBox.Ok)
        mensaje.exec()
        if mensaje.clickedButton() is abrir_logs_btn:
            self._abrir_carpeta("logs")

    def _manejar_excepcion_visual(self, exc: Exception, mensaje_usuario: str) -> None:
        detalle = traceback.format_exc()
        LOGGER.error("Excepción no controlada en wizard: %s", exc)
        LOGGER.debug("Stacktrace wizard:\n%s", detalle)
        logs_dir = Path("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        with (logs_dir / "crashes.log").open("a", encoding="utf-8") as file:
            file.write(f"\n{detalle}\n")
        QMessageBox.critical(self, "Error", mensaje_usuario)

    def _abrir_carpeta(self, ruta: str) -> None:
        url = QUrl.fromLocalFile(str(Path(ruta).resolve()))
        if not QDesktopServices.openUrl(url):
            QMessageBox.warning(self, "Abrir carpeta", f"No se pudo abrir: {ruta}")

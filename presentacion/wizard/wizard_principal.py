"""Wizard principal para configurar generación de proyectos (MVP)."""

from __future__ import annotations

import logging

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWizard

from aplicacion.casos_uso.construir_especificacion_proyecto import ConstruirEspecificacionProyecto
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import (
    GenerarProyectoMvp,
    GenerarProyectoMvpEntrada,
    GenerarProyectoMvpSalida,
)
from aplicacion.casos_uso.presets import CargarPresetProyecto, GuardarPresetProyecto
from aplicacion.casos_uso.seguridad import GuardarCredencial
from aplicacion.dtos.proyecto import DtoAtributo, DtoClase
from presentacion.trabajadores.trabajador_generacion import TrabajadorGeneracionMvp
from presentacion.wizard.controlador.controlador_wizard import ControladorWizardProyecto as ControladorBase
from presentacion.wizard.estado.estado_wizard import EstadoWizardProyecto
from presentacion.wizard.paginas.pagina_clases import PaginaClases
from presentacion.wizard.paginas.pagina_datos_proyecto import PaginaDatosProyecto
from presentacion.wizard.paginas.pagina_persistencia import PaginaPersistencia
from presentacion.wizard.paginas.pagina_resumen import PaginaResumen
from presentacion.wizard.servicios_ui.servicio_dialogos import ServicioDialogos

LOGGER = logging.getLogger(__name__)

BLUEPRINTS_MVP = ["base_clean_arch", "crud_json"]


class ControladorWizardProyecto(ControladorBase):
    """Adaptador de compatibilidad para construir DTO desde la vista."""

    def construir_dto(self, wizard: "WizardGeneradorProyectos"):
        return self.construir_dto_desde_estado(wizard.estado_actual())


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
        self._dialogos = ServicioDialogos()
        self._pool = QThreadPool.globalInstance()
        self._trabajador_activo: TrabajadorGeneracionMvp | None = None
        self._generador_mvp = generar_proyecto
        self._guardar_preset = guardar_preset
        self._cargar_preset = cargar_preset
        self._guardar_credencial = guardar_credencial
        self._catalogo_blueprints = catalogo_blueprints
        self._constructor_especificacion = ConstruirEspecificacionProyecto()

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

    def estado_actual(self) -> EstadoWizardProyecto:
        return EstadoWizardProyecto(
            nombre=self.pagina_datos.campo_nombre.text().strip(),
            ruta=self.pagina_datos.campo_ruta.text().strip(),
            descripcion=self.pagina_datos.campo_descripcion.text().strip(),
            version=self.pagina_datos.campo_version.text().strip(),
            clases=self.pagina_clases.dto_clases(),
            persistencia=self.pagina_persistencia.persistencia_seleccionada(),
            usuario_credencial=self.pagina_persistencia.usuario_credencial(),
            secreto_credencial=self.pagina_persistencia.secreto_credencial(),
            guardar_credencial=self.pagina_persistencia.guardar_credencial_segura(),
        )

    def _al_finalizar(self) -> None:
        dto = self._controlador.construir_dto_desde_estado(self.estado_actual())
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
                self._guardar_credencial.ejecutar_desde_datos(
                    identificador=identificador,
                    usuario=dto.usuario_credencial,
                    secreto=dto.secreto_credencial,
                    tipo=dto.persistencia,
                )
                LOGGER.info("Credencial almacenada de forma segura para identificador=%s", identificador)
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning(
                    "No se pudo persistir credencial en almacenamiento seguro. Se continuará solo en memoria. %s",
                    exc,
                )
                self._dialogos.advertir(
                    self,
                    "Credenciales",
                    "No se pudo guardar la credencial en el sistema seguro. Se usará únicamente en memoria durante esta ejecución.",
                )

        try:
            especificacion = self._constructor_especificacion.ejecutar(dto.proyecto)
        except Exception as exc:  # noqa: BLE001
            self._dialogos.error(self, "Error de validación", str(exc))
            return

        entrada = GenerarProyectoMvpEntrada(
            especificacion_proyecto=especificacion,
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
        nombre, aceptado = self._dialogos.pedir_texto(self, "Guardar preset", "Nombre del preset")
        if not aceptado:
            return

        nombre = nombre.strip()
        if not nombre:
            self._dialogos.advertir(self, "Guardar preset", "Debes indicar un nombre de preset.")
            return

        try:
            dto = self._controlador.construir_dto_desde_estado(self.estado_actual())
            ruta = self._guardar_preset.ejecutar_desde_dto(
                nombre=nombre,
                proyecto=dto.proyecto,
                blueprints=self._blueprints_seleccionados(),
                metadata={"persistencia": self.pagina_persistencia.persistencia_seleccionada()},
            )
            self._dialogos.informar(self, "Guardar preset", f"Preset guardado en: {ruta}")
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("No se pudo guardar preset: %s", exc)
            self._dialogos.error(self, "Guardar preset", str(exc))

    def _cargar_preset_desde_ui(self) -> None:
        try:
            nombres = self._cargar_preset._almacen.listar()  # noqa: SLF001
            if not nombres:
                self._dialogos.informar(self, "Cargar preset", "No hay presets disponibles.")
                return
            nombre, aceptado = self._dialogos.pedir_item(
                self,
                "Cargar preset",
                "Selecciona un preset",
                nombres,
            )
            if not aceptado:
                return
            preset = self._cargar_preset.ejecutar(nombre)
            self.aplicar_preset(preset)
            self._dialogos.informar(self, "Cargar preset", f"Preset '{nombre}' cargado.")
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("No se pudo cargar preset: %s", exc)
            self._dialogos.error(self, "Cargar preset", str(exc))

    def aplicar_preset(self, preset: object) -> None:
        especificacion = getattr(preset, "especificacion")
        self.pagina_datos.campo_nombre.setText(getattr(especificacion, "nombre_proyecto", ""))
        self.pagina_datos.campo_ruta.setText(getattr(especificacion, "ruta_destino", ""))
        self.pagina_datos.campo_descripcion.setText(getattr(especificacion, "descripcion", "") or "")
        self.pagina_datos.campo_version.setText(getattr(especificacion, "version", "0.1.0"))
        persistencia = str(getattr(preset, "metadata", {}).get("persistencia", "JSON"))
        self.pagina_persistencia.establecer_persistencia(persistencia)

        clases = []
        for clase in getattr(especificacion, "clases", []):
            atributos = [
                DtoAtributo(
                    nombre=atributo.nombre,
                    tipo=atributo.tipo,
                    obligatorio=atributo.obligatorio,
                )
                for atributo in getattr(clase, "atributos", [])
            ]
            clases.append(DtoClase(nombre=clase.nombre, atributos=atributos))
        self.pagina_clases.establecer_desde_dto(clases)

        self.pagina_persistencia.establecer_blueprints_disponibles(
            self._catalogo_blueprints,
            getattr(preset, "blueprints", []),
        )
        self.pagina_resumen.initializePage()

    def _blueprints_seleccionados(self) -> list[str]:
        seleccionados = self.pagina_persistencia.blueprints_seleccionados()
        if seleccionados:
            return seleccionados
        return BLUEPRINTS_MVP

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
            self._dialogos.informar(self, "Generación completada", mensaje)
            return

        detalle = "\n".join(salida.errores) if salida.errores else "Sin detalles adicionales"
        self._dialogos.advertir(
            self,
            "Generación completada con observaciones",
            f"{mensaje}\n\nSe detectaron errores críticos de auditoría:\n{detalle}",
        )

    def _on_generacion_error(self, mensaje: str, detalle: str) -> None:
        self._cambiar_estado_generando(False, "")
        LOGGER.error("Falló la generación desde wizard: %s | detalle=%s", mensaje, detalle)
        self._dialogos.error(
            self,
            "Error de generación",
            f"{mensaje}\n\nDetalle:\n{detalle}",
        )

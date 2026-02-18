"""Wizard principal para configurar y lanzar la generación de proyectos."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import traceback

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QTableView,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generar_manifest import GenerarManifest
from aplicacion.casos_uso.gestion_clases import (
    AgregarAtributo,
    AgregarClase,
    EditarAtributo,
    EliminarAtributo,
    EliminarClase,
    ListarClases,
    ObtenerClaseDetallada,
)
from dominio.modelos import ErrorValidacionDominio, EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto
from infraestructura.calculadora_hash_real import CalculadoraHashReal
from infraestructura.ejecutor_procesos_subprocess import EjecutorProcesosSubprocess
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.repositorio_especificacion_proyecto_en_memoria import RepositorioEspecificacionProyectoEnMemoria
from infraestructura.sistema_archivos_real import SistemaArchivosReal
from presentacion.modelos_qt.modelo_atributos import ModeloAtributos
from presentacion.modelos_qt.modelo_clases import ModeloClases
from presentacion.trabajadores.trabajador_generacion import ResultadoGeneracion, TrabajadorGeneracion

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DatosAtributoFormulario:
    nombre: str
    tipo: str
    obligatorio: bool
    valor_por_defecto: str | None


class DialogoAtributo(QDialog):
    def __init__(self, parent: QWidget | None = None, inicial: EspecificacionAtributo | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Atributo")
        layout = QFormLayout(self)

        self._nombre = QLineEdit(inicial.nombre if inicial else "")
        self._tipo = QLineEdit(inicial.tipo if inicial else "str")
        self._obligatorio = QCheckBox("Obligatorio")
        self._obligatorio.setChecked(inicial.obligatorio if inicial else True)
        self._valor = QLineEdit(inicial.valor_por_defecto or "" if inicial else "")

        layout.addRow("Nombre", self._nombre)
        layout.addRow("Tipo", self._tipo)
        layout.addRow("", self._obligatorio)
        layout.addRow("Valor por defecto", self._valor)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)

    def datos(self) -> DatosAtributoFormulario:
        valor = self._valor.text().strip()
        return DatosAtributoFormulario(
            nombre=self._nombre.text().strip(),
            tipo=self._tipo.text().strip(),
            obligatorio=self._obligatorio.isChecked(),
            valor_por_defecto=valor or None,
        )


class PaginaDatosProyecto(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Datos del proyecto")
        self.setSubTitle("Configura metadatos mínimos del proyecto.")

        layout = QFormLayout(self)

        self.nombre_proyecto = QLineEdit("proyecto_demo")
        self.ruta_destino = QLineEdit("salida/proyecto_demo")
        self.descripcion = QLineEdit("Proyecto generado con wizard PySide6")
        self.version = QLineEdit("0.5.0")

        boton_ruta = QPushButton("Seleccionar carpeta...")
        boton_ruta.clicked.connect(self._seleccionar_directorio)

        ruta_layout = QHBoxLayout()
        ruta_layout.addWidget(self.ruta_destino)
        ruta_layout.addWidget(boton_ruta)

        layout.addRow("Nombre proyecto", self.nombre_proyecto)
        layout.addRow("Ruta destino", ruta_layout)
        layout.addRow("Descripción", self.descripcion)
        layout.addRow("Versión", self.version)

    def _seleccionar_directorio(self) -> None:
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar ruta destino")
        if carpeta:
            self.ruta_destino.setText(carpeta)


class PaginaClases(QWizardPage):
    def __init__(self, repositorio: RepositorioEspecificacionProyectoEnMemoria) -> None:
        super().__init__()
        self.setTitle("Clases")
        self.setSubTitle("Gestiona clases y atributos del constructor dinámico.")

        self._repositorio = repositorio
        self._agregar_clase = AgregarClase(repositorio)
        self._eliminar_clase = EliminarClase(repositorio)
        self._agregar_atributo = AgregarAtributo(repositorio)
        self._editar_atributo = EditarAtributo(repositorio)
        self._eliminar_atributo = EliminarAtributo(repositorio)
        self._listar_clases = ListarClases(repositorio)
        self._obtener_clase = ObtenerClaseDetallada(repositorio)

        self._modelo_clases = ModeloClases([])
        self._modelo_atributos = ModeloAtributos([])

        self._tabla_clases = QTableView()
        self._tabla_clases.setModel(self._modelo_clases)
        self._tabla_clases.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_clases.selectionModel().selectionChanged.connect(
            self._actualizar_atributos_por_clase_seleccionada
        )

        self._tabla_atributos = QTableView()
        self._tabla_atributos.setModel(self._modelo_atributos)
        self._tabla_atributos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        botones_clase = QHBoxLayout()
        boton_anadir_clase = QPushButton("Añadir clase")
        boton_anadir_clase.clicked.connect(self._on_anadir_clase)
        boton_eliminar_clase = QPushButton("Eliminar clase")
        boton_eliminar_clase.clicked.connect(self._on_eliminar_clase)
        botones_clase.addWidget(boton_anadir_clase)
        botones_clase.addWidget(boton_eliminar_clase)

        botones_attr = QHBoxLayout()
        boton_anadir_atributo = QPushButton("Añadir atributo")
        boton_anadir_atributo.clicked.connect(self._on_anadir_atributo)
        boton_editar_atributo = QPushButton("Editar atributo")
        boton_editar_atributo.clicked.connect(self._on_editar_atributo)
        boton_eliminar_atributo = QPushButton("Eliminar atributo")
        boton_eliminar_atributo.clicked.connect(self._on_eliminar_atributo)
        botones_attr.addWidget(boton_anadir_atributo)
        botones_attr.addWidget(boton_editar_atributo)
        botones_attr.addWidget(boton_eliminar_atributo)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Clases"))
        layout.addWidget(self._tabla_clases)
        layout.addLayout(botones_clase)
        layout.addWidget(QLabel("Atributos de la clase seleccionada"))
        layout.addWidget(self._tabla_atributos)
        layout.addLayout(botones_attr)

    def initializePage(self) -> None:  # noqa: N802
        self._refrescar_modelos()

    def _mostrar_error(self, exc: Exception) -> None:
        LOGGER.error("Error en página de clases: %s", exc)
        LOGGER.debug("Stacktrace UI clases:\n%s", traceback.format_exc())
        QMessageBox.critical(self, "Error", str(exc))

    def _refrescar_modelos(self) -> None:
        clases = self._listar_clases.ejecutar()
        self._modelo_clases.actualizar(clases)
        self._modelo_atributos.actualizar([])

    def _clase_seleccionada(self) -> EspecificacionClase | None:
        indice = self._tabla_clases.currentIndex()
        return self._modelo_clases.clase_en_fila(indice.row())

    def _atributo_seleccionado(self) -> EspecificacionAtributo | None:
        indice = self._tabla_atributos.currentIndex()
        return self._modelo_atributos.atributo_en_fila(indice.row())

    def _actualizar_atributos_por_clase_seleccionada(self) -> None:
        clase = self._clase_seleccionada()
        if clase is None:
            self._modelo_atributos.actualizar([])
            return
        clase_detalle = self._obtener_clase.ejecutar(clase.id_interno)
        self._modelo_atributos.actualizar(clase_detalle.atributos)

    def _on_anadir_clase(self) -> None:
        nombre, confirmado = QInputDialog.getText(self, "Nueva clase", "Nombre (PascalCase):")
        if not confirmado:
            return
        try:
            self._agregar_clase.ejecutar(EspecificacionClase(nombre=nombre.strip()))
            self._refrescar_modelos()
        except (ErrorValidacionDominio, ValueError) as exc:
            self._mostrar_error(exc)

    def _on_eliminar_clase(self) -> None:
        clase = self._clase_seleccionada()
        if clase is None:
            return
        try:
            self._eliminar_clase.ejecutar(clase.id_interno)
            self._refrescar_modelos()
        except (ErrorValidacionDominio, ValueError) as exc:
            self._mostrar_error(exc)

    def _on_anadir_atributo(self) -> None:
        clase = self._clase_seleccionada()
        if clase is None:
            return
        dialogo = DialogoAtributo(self)
        if dialogo.exec() != QDialog.Accepted:
            return
        try:
            datos = dialogo.datos()
            atributo = EspecificacionAtributo(
                nombre=datos.nombre,
                tipo=datos.tipo,
                obligatorio=datos.obligatorio,
                valor_por_defecto=datos.valor_por_defecto,
            )
            self._agregar_atributo.ejecutar(clase.id_interno, atributo)
            self._actualizar_atributos_por_clase_seleccionada()
        except (ErrorValidacionDominio, ValueError) as exc:
            self._mostrar_error(exc)

    def _on_editar_atributo(self) -> None:
        clase = self._clase_seleccionada()
        atributo = self._atributo_seleccionado()
        if clase is None or atributo is None:
            return
        dialogo = DialogoAtributo(self, inicial=atributo)
        if dialogo.exec() != QDialog.Accepted:
            return
        try:
            datos = dialogo.datos()
            self._editar_atributo.ejecutar(
                id_clase=clase.id_interno,
                id_atributo=atributo.id_interno,
                nombre=datos.nombre,
                tipo=datos.tipo,
                obligatorio=datos.obligatorio,
                valor_por_defecto=datos.valor_por_defecto,
            )
            self._actualizar_atributos_por_clase_seleccionada()
        except (ErrorValidacionDominio, ValueError) as exc:
            self._mostrar_error(exc)

    def _on_eliminar_atributo(self) -> None:
        clase = self._clase_seleccionada()
        atributo = self._atributo_seleccionado()
        if clase is None or atributo is None:
            return
        try:
            self._eliminar_atributo.ejecutar(clase.id_interno, atributo.id_interno)
            self._actualizar_atributos_por_clase_seleccionada()
        except (ErrorValidacionDominio, ValueError) as exc:
            self._mostrar_error(exc)


class PaginaBlueprints(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Blueprints")
        self.setSubTitle("Selecciona blueprints a ejecutar.")

        self.base_clean_arch = QCheckBox("base_clean_arch (obligatorio)")
        self.base_clean_arch.setChecked(True)
        self.base_clean_arch.setEnabled(False)

        self.crud_json = QCheckBox("crud_json")
        self.crud_json.setChecked(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.base_clean_arch)
        layout.addWidget(self.crud_json)

    def blueprints_seleccionados(self) -> list[str]:
        blueprints = ["base_clean_arch"]
        if self.crud_json.isChecked():
            blueprints.append("crud_json")
        return blueprints


class PaginaResumen(QWizardPage):
    def __init__(self, wizard: "WizardProyecto") -> None:
        super().__init__()
        self._wizard_raiz = wizard
        self.setTitle("Resumen")
        self.setSubTitle("Verifica la configuración antes de generar.")

        layout = QVBoxLayout(self)
        self._resumen = QPlainTextEdit()
        self._resumen.setReadOnly(True)
        layout.addWidget(self._resumen)

        self._progreso_label = QLabel("Listo para generar.")
        self._progreso_barra = QProgressBar()
        self._progreso_barra.setRange(0, 1)
        self._progreso_barra.setValue(0)
        layout.addWidget(self._progreso_label)
        layout.addWidget(self._progreso_barra)

        self.boton_generar = QPushButton("Generar")
        self.boton_generar.clicked.connect(self._wizard_raiz.generar_en_background)
        layout.addWidget(self.boton_generar)

    def initializePage(self) -> None:  # noqa: N802
        self._resumen.setPlainText(self._wizard_raiz.construir_resumen())

    def actualizar_progreso(self, texto: str) -> None:
        self._progreso_label.setText(texto)
        self._progreso_barra.setRange(0, 0)

    def marcar_finalizado(self) -> None:
        self._progreso_barra.setRange(0, 1)
        self._progreso_barra.setValue(1)


class WizardProyecto(QWizard):
    def __init__(self, version_generador: str) -> None:
        super().__init__()
        self.setWindowTitle("Generador Base Proyectos - Wizard")
        self.resize(1000, 680)

        self._version_generador = version_generador
        self._thread_pool = QThreadPool.globalInstance()
        self._repositorio_estado = RepositorioEspecificacionProyectoEnMemoria(
            EspecificacionProyecto(
                nombre_proyecto="proyecto_demo",
                ruta_destino="salida/proyecto_demo",
                descripcion="Proyecto generado desde wizard",
                version=version_generador,
            )
        )

        self.pagina_datos = PaginaDatosProyecto()
        self.pagina_clases = PaginaClases(self._repositorio_estado)
        self.pagina_blueprints = PaginaBlueprints()
        self.pagina_resumen = PaginaResumen(self)

        self.addPage(self.pagina_datos)
        self.addPage(self.pagina_clases)
        self.addPage(self.pagina_blueprints)
        self.addPage(self.pagina_resumen)

    def construir_resumen(self) -> str:
        especificacion = self._actualizar_especificacion_desde_formulario()
        blueprints = self.pagina_blueprints.blueprints_seleccionados()
        clases = [f"- {clase.nombre} ({len(clase.atributos)} atributos)" for clase in especificacion.clases]
        clases_txt = "\n".join(clases) if clases else "- Sin clases"
        return (
            f"Proyecto: {especificacion.nombre_proyecto}\n"
            f"Ruta: {especificacion.ruta_destino}\n"
            f"Descripción: {especificacion.descripcion or '-'}\n"
            f"Versión: {especificacion.version}\n"
            f"Blueprints: {', '.join(blueprints)}\n"
            f"Clases:\n{clases_txt}"
        )

    def _actualizar_especificacion_desde_formulario(self) -> EspecificacionProyecto:
        estado = self._repositorio_estado.obtener()
        estado.nombre_proyecto = self.pagina_datos.nombre_proyecto.text().strip()
        estado.ruta_destino = self.pagina_datos.ruta_destino.text().strip()
        estado.descripcion = self.pagina_datos.descripcion.text().strip()
        estado.version = self.pagina_datos.version.text().strip()
        estado.validar()
        self._repositorio_estado.guardar(estado)
        return estado

    def _set_controles_habilitados(self, habilitado: bool) -> None:
        self.button(QWizard.NextButton).setEnabled(habilitado)
        self.button(QWizard.BackButton).setEnabled(habilitado)
        self.button(QWizard.CancelButton).setEnabled(habilitado)
        self.pagina_resumen.boton_generar.setEnabled(habilitado)

    def generar_en_background(self) -> None:
        try:
            especificacion = self._actualizar_especificacion_desde_formulario()
        except (ErrorValidacionDominio, ValueError) as exc:
            QMessageBox.critical(self, "Datos inválidos", str(exc))
            return

        blueprints = self.pagina_blueprints.blueprints_seleccionados()
        LOGGER.info("Inicio generación proyecto=%s", especificacion.nombre_proyecto)
        LOGGER.info("Blueprints seleccionados: %s", blueprints)

        worker = TrabajadorGeneracion(
            especificacion=especificacion,
            blueprints=blueprints,
            crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco()),
            ejecutar_plan=EjecutarPlan(
                sistema_archivos=SistemaArchivosReal(),
                generador_manifest=GenerarManifest(CalculadoraHashReal()),
            ),
            auditor=AuditarProyectoGenerado(EjecutorProcesosSubprocess()),
            version_generador=self._version_generador,
        )

        worker.senales.progreso.connect(self.pagina_resumen.actualizar_progreso)
        worker.senales.finalizado.connect(self._on_generacion_finalizada)
        worker.senales.error.connect(self._on_generacion_error)

        self._set_controles_habilitados(False)
        self.pagina_resumen.actualizar_progreso("Preparando ejecución...")
        self._thread_pool.start(worker)

    def _on_generacion_finalizada(self, resultado: ResultadoGeneracion) -> None:
        self._set_controles_habilitados(True)
        self.pagina_resumen.marcar_finalizado()
        LOGGER.info(
            "Resultado auditoría en UI: valido=%s cobertura=%s resumen=%s errores=%s",
            resultado.auditoria.valido,
            resultado.auditoria.cobertura,
            resultado.auditoria.resumen,
            resultado.auditoria.lista_errores,
        )
        if resultado.auditoria.valido:
            QMessageBox.information(
                self,
                "Generación finalizada",
                f"Proyecto generado correctamente en:\n{resultado.ruta_destino}\n\n{resultado.auditoria.resumen}",
            )
            return
        LOGGER.error("Auditoría rechazada. Detalles enviados a crashes.log: %s", resultado.auditoria.lista_errores)
        QMessageBox.warning(
            self,
            "Auditoría RECHAZADA",
            f"{resultado.auditoria.resumen}\n\n" + "\n".join(resultado.auditoria.lista_errores),
        )

    def _on_generacion_error(self, error: Exception) -> None:
        self._set_controles_habilitados(True)
        self.pagina_resumen.marcar_finalizado()
        LOGGER.error("Error en generación background: %s", error)
        LOGGER.debug("Stacktrace error UI:\n%s", traceback.format_exc())
        QMessageBox.critical(self, "Error en generación", str(error))

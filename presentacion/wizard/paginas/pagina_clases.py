"""Página para capturar clases y atributos del proyecto en el wizard."""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWizardPage,
)

from aplicacion.dtos.proyecto import DtoAtributo, DtoClase

LOGGER = logging.getLogger(__name__)


class PaginaClases(QWizardPage):
    """Permite añadir, editar y eliminar clases y atributos en el wizard."""

    TIPOS_ATRIBUTO = ("str", "int", "float", "bool")

    def __init__(self) -> None:
        super().__init__()
        self._crear_widgets()
        self._configurar_layout()
        self._configurar_modelos()
        self._conectar_senales()
        self._inicializar_estado()

    def _crear_widgets(self) -> None:
        self.setTitle("Clases")
        self.setSubTitle("Añade clases y sus atributos iniciales.")
        self._campo_nombre_clase = QLineEdit()
        self._campo_nombre_clase.setPlaceholderText("Nombre de clase")
        self._lista_clases = QListWidget()
        self._boton_anadir_clase = QPushButton("Añadir clase")
        self._boton_eliminar_clase = QPushButton("Eliminar clase")

        self._tabla_atributos = QTableWidget(0, 3)
        self._tabla_atributos.setHorizontalHeaderLabels(["Nombre", "Tipo", "Obligatorio"])
        self._tabla_atributos.horizontalHeader().setStretchLastSection(True)
        self._tabla_atributos.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_atributos.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_atributos.setSelectionMode(QTableWidget.SingleSelection)
        self._campo_nombre_atributo = QLineEdit()
        self._campo_nombre_atributo.setPlaceholderText("Nombre de atributo")
        self._combo_tipo_atributo = QComboBox()
        self._combo_tipo_atributo.addItems(self.TIPOS_ATRIBUTO)
        self._checkbox_obligatorio = QCheckBox("Obligatorio")
        self._boton_anadir_atributo = QPushButton("Añadir atributo")
        self._boton_eliminar_atributo = QPushButton("Eliminar atributo")

    def _configurar_layout(self) -> None:
        panel_izquierdo = self._construir_panel_clases()
        panel_derecho = self._construir_panel_atributos()

        layout_principal = QHBoxLayout(self)
        layout_principal.addLayout(panel_izquierdo)
        layout_principal.addLayout(panel_derecho)

    def _construir_panel_clases(self) -> QVBoxLayout:
        panel_izquierdo = QVBoxLayout()
        panel_izquierdo.addWidget(self._lista_clases)

        fila_controles_clase = QHBoxLayout()
        fila_controles_clase.addWidget(self._campo_nombre_clase)
        fila_controles_clase.addWidget(self._boton_anadir_clase)
        panel_izquierdo.addLayout(fila_controles_clase)
        panel_izquierdo.addWidget(self._boton_eliminar_clase)
        return panel_izquierdo

    def _construir_panel_atributos(self) -> QVBoxLayout:
        panel_derecho = QVBoxLayout()
        panel_derecho.addWidget(self._tabla_atributos)

        fila_controles_atributo = QHBoxLayout()
        fila_controles_atributo.addWidget(self._campo_nombre_atributo)
        fila_controles_atributo.addWidget(self._combo_tipo_atributo)
        fila_controles_atributo.addWidget(self._checkbox_obligatorio)
        fila_controles_atributo.addWidget(self._boton_anadir_atributo)
        panel_derecho.addLayout(fila_controles_atributo)
        panel_derecho.addWidget(self._boton_eliminar_atributo)
        return panel_derecho

    def _configurar_modelos(self) -> None:
        self._clases_dto: list[DtoClase] = []

    def _conectar_senales(self) -> None:
        self._lista_clases.currentRowChanged.connect(self._al_cambiar_clase_seleccionada)
        self._boton_anadir_clase.clicked.connect(self.anadir_clase_desde_input)
        self._boton_eliminar_clase.clicked.connect(self.eliminar_clase_seleccionada)
        self._boton_anadir_atributo.clicked.connect(self.anadir_atributo_desde_input)
        self._boton_eliminar_atributo.clicked.connect(self.eliminar_atributo_seleccionado)

    def _inicializar_estado(self) -> None:
        self._widgets_panel_atributos = [
            self._tabla_atributos,
            self._campo_nombre_atributo,
            self._combo_tipo_atributo,
            self._checkbox_obligatorio,
            self._boton_anadir_atributo,
            self._boton_eliminar_atributo,
        ]
        self._actualizar_estado_panel_atributos(False)
        self._estado_complete = self._calcular_estado_complete_ui()

    def isComplete(self) -> bool:  # noqa: N802
        return self._calcular_estado_complete_ui()

    def anadir_clase_desde_input(self) -> bool:
        return self.anadir_clase(self._campo_nombre_clase.text())

    def anadir_clase(self, nombre_clase: str) -> bool:
        nombre_limpio = self._normalizar_nombre(nombre_clase)
        if nombre_limpio is None:
            return False

        if any(clase.nombre == nombre_limpio for clase in self._clases_dto):
            QMessageBox.critical(self, "Error de validación", f"Ya existe una clase con nombre '{nombre_limpio}'.")
            return False

        self._clases_dto.append(DtoClase(nombre=nombre_limpio))
        self._lista_clases.addItem(QListWidgetItem(nombre_limpio))
        self._campo_nombre_clase.clear()
        self._lista_clases.setCurrentRow(self._lista_clases.count() - 1)
        self._emitir_cambio_completitud()
        return True

    def eliminar_clase_seleccionada(self) -> bool:
        indice = self._lista_clases.currentRow()
        if indice < 0:
            return False

        self._clases_dto.pop(indice)
        self._lista_clases.takeItem(indice)
        self._tabla_atributos.setRowCount(0)

        if self._lista_clases.count() > 0:
            siguiente = min(indice, self._lista_clases.count() - 1)
            self._lista_clases.setCurrentRow(siguiente)
            self._actualizar_estado_panel_atributos(True)
        else:
            self._actualizar_estado_panel_atributos(False)

        self._emitir_cambio_completitud()
        return True

    def anadir_atributo_desde_input(self) -> bool:
        return self.anadir_atributo(
            nombre_atributo=self._campo_nombre_atributo.text(),
            tipo=self._combo_tipo_atributo.currentText(),
            obligatorio=self._checkbox_obligatorio.isChecked(),
        )

    def anadir_atributo(self, nombre_atributo: str, tipo: str, obligatorio: bool) -> bool:
        clase, indice_clase = self._clase_seleccionada()
        if clase is None:
            return False

        nombre_limpio = self._normalizar_nombre(nombre_atributo)
        if nombre_limpio is None:
            return False

        if any(atributo.nombre == nombre_limpio for atributo in clase.atributos):
            QMessageBox.critical(self, "Error de validación", f"Ya existe un atributo con nombre '{nombre_limpio}'.")
            return False

        atributos = [
            *clase.atributos,
            DtoAtributo(nombre=nombre_limpio, tipo=tipo, obligatorio=obligatorio),
        ]
        self._clases_dto[indice_clase] = DtoClase(nombre=clase.nombre, atributos=atributos)
        self._renderizar_atributos(self._clases_dto[indice_clase])
        self._campo_nombre_atributo.clear()
        self._checkbox_obligatorio.setChecked(False)
        return True

    def eliminar_atributo_seleccionado(self) -> bool:
        clase, indice_clase = self._clase_seleccionada()
        if clase is None:
            return False

        fila = self._tabla_atributos.currentRow()
        if fila < 0 or fila >= len(clase.atributos):
            return False

        atributos = [*clase.atributos]
        atributos.pop(fila)
        self._clases_dto[indice_clase] = DtoClase(nombre=clase.nombre, atributos=atributos)
        self._renderizar_atributos(self._clases_dto[indice_clase])
        if self._tabla_atributos.rowCount() > 0:
            self._tabla_atributos.setCurrentCell(min(fila, self._tabla_atributos.rowCount() - 1), 0)
        return True

    def clases(self) -> list[str]:
        return [clase.nombre for clase in self._clases_dto]

    def dto_clases(self) -> list[DtoClase]:
        return [DtoClase(nombre=clase.nombre, atributos=[*clase.atributos]) for clase in self._clases_dto]

    def establecer_desde_dto(self, clases: list[DtoClase]) -> None:
        self._clases_dto = [DtoClase(nombre=clase.nombre, atributos=[*clase.atributos]) for clase in clases]
        self._lista_clases.clear()
        for clase in self._clases_dto:
            self._lista_clases.addItem(QListWidgetItem(clase.nombre))
        if self._lista_clases.count() > 0:
            self._lista_clases.setCurrentRow(0)
            self._actualizar_estado_panel_atributos(True)
            self._renderizar_atributos(self._clases_dto[0])
        else:
            self._actualizar_estado_panel_atributos(False)
            self._tabla_atributos.setRowCount(0)
        self._emitir_cambio_completitud()

    def seleccionar_atributo(self, indice: int) -> bool:
        if indice < 0 or indice >= self._tabla_atributos.rowCount():
            return False
        self._tabla_atributos.setCurrentCell(indice, 0)
        return True

    def panel_atributos_habilitado(self) -> bool:
        return self._tabla_atributos.isEnabled()

    def limpiar_seleccion_clase(self) -> None:
        self._lista_clases.clearSelection()
        self._lista_clases.setCurrentRow(-1)

    def _normalizar_nombre(self, valor: str) -> str | None:
        nombre = valor.strip()
        if not nombre:
            QMessageBox.critical(self, "Error de validación", "El nombre no puede estar vacío.")
            return None
        return nombre

    def _clase_seleccionada(self) -> tuple[DtoClase | None, int]:
        indice = self._lista_clases.currentRow()
        if indice < 0 or indice >= len(self._clases_dto):
            return None, -1
        return self._clases_dto[indice], indice

    def _al_cambiar_clase_seleccionada(self, indice: int) -> None:
        if indice < 0 or indice >= len(self._clases_dto):
            self._actualizar_estado_panel_atributos(False)
            self._tabla_atributos.setRowCount(0)
            return
        self._actualizar_estado_panel_atributos(True)
        self._renderizar_atributos(self._clases_dto[indice])

    def _actualizar_estado_panel_atributos(self, habilitado: bool) -> None:
        for widget in self._widgets_panel_atributos:
            widget.setEnabled(habilitado)

    def _renderizar_atributos(self, clase: DtoClase | None) -> None:
        self._tabla_atributos.setRowCount(0)
        if clase is None:
            return

        for fila, atributo in enumerate(clase.atributos):
            self._tabla_atributos.insertRow(fila)
            self._tabla_atributos.setItem(fila, 0, QTableWidgetItem(atributo.nombre))
            self._tabla_atributos.setItem(fila, 1, QTableWidgetItem(atributo.tipo))
            item_obligatorio = QTableWidgetItem("Sí" if atributo.obligatorio else "No")
            item_obligatorio.setTextAlignment(Qt.AlignCenter)
            self._tabla_atributos.setItem(fila, 2, item_obligatorio)

    def _calcular_estado_complete_ui(self) -> bool:
        return self._lista_clases.count() > 0

    def _emitir_cambio_completitud(self) -> None:
        estado_actual = self._calcular_estado_complete_ui()
        if estado_actual != self._estado_complete:
            self._estado_complete = estado_actual
        self.completeChanged.emit()

"""Página para capturar clases y atributos del dominio en el wizard."""

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
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWizardPage,
)

from presentacion.wizard.modelos.modelo_clases_temporal import AtributoTemporal, ClaseTemporal

LOGGER = logging.getLogger(__name__)


class PaginaClases(QWizardPage):
    """Permite añadir, editar y eliminar clases y atributos en el wizard."""

    TIPOS_ATRIBUTO = ("str", "int", "float", "bool")

    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Clases")
        self.setSubTitle("Añade clases y sus atributos iniciales.")

        self._clases_temporales: list[ClaseTemporal] = []

        self._campo_nombre_clase = QLineEdit()
        self._campo_nombre_clase.setPlaceholderText("Nombre de clase")

        self._lista_clases = QListWidget()
        self._lista_clases.currentRowChanged.connect(self._al_cambiar_clase_seleccionada)

        boton_anadir_clase = QPushButton("Añadir clase")
        boton_anadir_clase.clicked.connect(self.anadir_clase_desde_input)

        boton_eliminar_clase = QPushButton("Eliminar clase")
        boton_eliminar_clase.clicked.connect(self.eliminar_clase_seleccionada)

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

        boton_anadir_atributo = QPushButton("Añadir atributo")
        boton_anadir_atributo.clicked.connect(self.anadir_atributo_desde_input)

        boton_eliminar_atributo = QPushButton("Eliminar atributo")
        boton_eliminar_atributo.clicked.connect(self.eliminar_atributo_seleccionado)

        panel_izquierdo = QVBoxLayout()
        panel_izquierdo.addWidget(self._lista_clases)

        fila_controles_clase = QHBoxLayout()
        fila_controles_clase.addWidget(self._campo_nombre_clase)
        fila_controles_clase.addWidget(boton_anadir_clase)
        panel_izquierdo.addLayout(fila_controles_clase)
        panel_izquierdo.addWidget(boton_eliminar_clase)

        panel_derecho = QVBoxLayout()
        panel_derecho.addWidget(self._tabla_atributos)

        fila_controles_atributo = QHBoxLayout()
        fila_controles_atributo.addWidget(self._campo_nombre_atributo)
        fila_controles_atributo.addWidget(self._combo_tipo_atributo)
        fila_controles_atributo.addWidget(self._checkbox_obligatorio)
        fila_controles_atributo.addWidget(boton_anadir_atributo)
        panel_derecho.addLayout(fila_controles_atributo)
        panel_derecho.addWidget(boton_eliminar_atributo)

        layout_principal = QHBoxLayout(self)
        layout_principal.addLayout(panel_izquierdo)
        layout_principal.addLayout(panel_derecho)

        self._widgets_panel_atributos = [
            self._tabla_atributos,
            self._campo_nombre_atributo,
            self._combo_tipo_atributo,
            self._checkbox_obligatorio,
            boton_anadir_atributo,
            boton_eliminar_atributo,
        ]
        self._actualizar_estado_panel_atributos(False)

    def anadir_clase_desde_input(self) -> bool:
        return self.anadir_clase(self._campo_nombre_clase.text())

    def anadir_clase(self, nombre_clase: str) -> bool:
        nombre_limpio = self._normalizar_nombre(nombre_clase)
        if nombre_limpio is None:
            return False
        if self._buscar_clase(nombre_limpio) is not None:
            return False

        self._clases_temporales.append(ClaseTemporal(nombre=nombre_limpio))
        self._lista_clases.addItem(QListWidgetItem(nombre_limpio))
        self._campo_nombre_clase.clear()
        self._lista_clases.setCurrentRow(self._lista_clases.count() - 1)
        LOGGER.debug("Clase añadida: %s", nombre_limpio)
        return True

    def eliminar_clase_seleccionada(self) -> bool:
        indice = self._indice_clase_seleccionada()
        if indice is None:
            return False

        clase_eliminada = self._clases_temporales.pop(indice)
        self._lista_clases.takeItem(indice)
        LOGGER.debug("Clase eliminada: %s", clase_eliminada.nombre)
        return True

    def anadir_atributo_desde_input(self) -> bool:
        return self.anadir_atributo(
            nombre_atributo=self._campo_nombre_atributo.text(),
            tipo=self._combo_tipo_atributo.currentText(),
            obligatorio=self._checkbox_obligatorio.isChecked(),
        )

    def anadir_atributo(self, *, nombre_atributo: str, tipo: str, obligatorio: bool) -> bool:
        indice = self._indice_clase_seleccionada()
        if indice is None:
            return False

        nombre_limpio = self._normalizar_nombre(nombre_atributo)
        if nombre_limpio is None:
            return False

        clase = self._clases_temporales[indice]
        if any(atributo.nombre == nombre_limpio for atributo in clase.atributos):
            return False

        atributo = AtributoTemporal(nombre=nombre_limpio, tipo=tipo, obligatorio=obligatorio)
        clase.atributos.append(atributo)
        self._campo_nombre_atributo.clear()
        self._checkbox_obligatorio.setChecked(False)
        self._renderizar_atributos(clase)
        LOGGER.debug("Atributo añadido: %s.%s", clase.nombre, atributo.nombre)
        return True

    def eliminar_atributo_seleccionado(self) -> bool:
        indice_clase = self._indice_clase_seleccionada()
        if indice_clase is None:
            return False

        fila_atributo = self._tabla_atributos.currentRow()
        if fila_atributo < 0:
            return False

        clase = self._clases_temporales[indice_clase]
        if fila_atributo >= len(clase.atributos):
            return False

        atributo_eliminado = clase.atributos.pop(fila_atributo)
        self._renderizar_atributos(clase)
        LOGGER.debug("Atributo eliminado: %s.%s", clase.nombre, atributo_eliminado.nombre)
        return True

    def clases(self) -> list[str]:
        return [clase.nombre for clase in self._clases_temporales]

    def clases_temporales(self) -> list[ClaseTemporal]:
        return [
            ClaseTemporal(
                nombre=clase.nombre,
                atributos=[
                    AtributoTemporal(
                        nombre=atributo.nombre,
                        tipo=atributo.tipo,
                        obligatorio=atributo.obligatorio,
                    )
                    for atributo in clase.atributos
                ],
            )
            for clase in self._clases_temporales
        ]

    def panel_atributos_habilitado(self) -> bool:
        return self._tabla_atributos.isEnabled()

    def seleccionar_atributo(self, indice_fila: int) -> bool:
        if indice_fila < 0 or indice_fila >= self._tabla_atributos.rowCount():
            return False
        self._tabla_atributos.setCurrentCell(indice_fila, 0)
        return True

    def limpiar_seleccion_clase(self) -> None:
        self._lista_clases.setCurrentRow(-1)

    def _indice_clase_seleccionada(self) -> int | None:
        indice = self._lista_clases.currentRow()
        if indice < 0 or indice >= len(self._clases_temporales):
            return None
        return indice

    def _buscar_clase(self, nombre_clase: str) -> ClaseTemporal | None:
        for clase in self._clases_temporales:
            if clase.nombre == nombre_clase:
                return clase
        return None

    def _normalizar_nombre(self, nombre: str) -> str | None:
        nombre_limpio = nombre.strip()
        if not nombre_limpio:
            return None
        if " " in nombre_limpio:
            return None
        return nombre_limpio

    def _al_cambiar_clase_seleccionada(self, _: int) -> None:
        indice = self._indice_clase_seleccionada()
        if indice is None:
            self._actualizar_estado_panel_atributos(False)
            self._renderizar_atributos(None)
            return

        self._actualizar_estado_panel_atributos(True)
        self._renderizar_atributos(self._clases_temporales[indice])

    def _actualizar_estado_panel_atributos(self, habilitado: bool) -> None:
        for widget in self._widgets_panel_atributos:
            widget.setEnabled(habilitado)

    def _renderizar_atributos(self, clase: ClaseTemporal | None) -> None:
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

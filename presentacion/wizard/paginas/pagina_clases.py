"""Página para capturar clases del dominio en el wizard."""

from __future__ import annotations

import logging

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QListWidget, QPushButton, QVBoxLayout, QWizardPage

LOGGER = logging.getLogger(__name__)


class PaginaClases(QWizardPage):
    """Permite añadir y eliminar clases de forma superficial para el MVP."""

    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Clases")
        self.setSubTitle("Añade las clases iniciales del proyecto.")

        self._campo_nombre_clase = QLineEdit()
        self._lista_clases = QListWidget()

        boton_anadir = QPushButton("Añadir clase")
        boton_anadir.clicked.connect(self.anadir_clase_desde_input)

        boton_eliminar = QPushButton("Eliminar clase seleccionada")
        boton_eliminar.clicked.connect(self.eliminar_clase_seleccionada)

        fila_controles = QHBoxLayout()
        fila_controles.addWidget(self._campo_nombre_clase)
        fila_controles.addWidget(boton_anadir)

        layout = QVBoxLayout(self)
        layout.addLayout(fila_controles)
        layout.addWidget(self._lista_clases)
        layout.addWidget(boton_eliminar)

    def anadir_clase_desde_input(self) -> bool:
        return self.anadir_clase(self._campo_nombre_clase.text())

    def anadir_clase(self, nombre_clase: str) -> bool:
        nombre_limpio = nombre_clase.strip()
        if not nombre_limpio:
            LOGGER.info("Validación superficial: nombre de clase vacío")
            return False
        if " " in nombre_limpio:
            LOGGER.info("Validación superficial: nombre de clase con espacios")
            return False
        if nombre_limpio in self.clases():
            LOGGER.info("Validación superficial: clase duplicada (%s)", nombre_limpio)
            return False

        self._lista_clases.addItem(nombre_limpio)
        self._campo_nombre_clase.clear()
        return True

    def eliminar_clase_seleccionada(self) -> None:
        fila = self._lista_clases.currentRow()
        if fila >= 0:
            self._lista_clases.takeItem(fila)

    def clases(self) -> list[str]:
        return [self._lista_clases.item(indice).text() for indice in range(self._lista_clases.count())]

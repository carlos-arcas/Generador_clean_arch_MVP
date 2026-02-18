"""Página de datos básicos del proyecto para el wizard."""

from __future__ import annotations

import logging

from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWizardPage,
)

LOGGER = logging.getLogger(__name__)


class PaginaDatosProyecto(QWizardPage):
    """Captura datos mínimos del proyecto a generar."""

    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Datos del proyecto")
        self.setSubTitle("Define nombre, ruta y metadatos básicos.")

        self.campo_nombre = QLineEdit()
        self.campo_ruta = QLineEdit()
        self.campo_descripcion = QLineEdit()
        self.campo_version = QLineEdit("1.0.1")
        self._estado_complete = self.isComplete()

        self.campo_nombre.textChanged.connect(self._on_cambio_campos)
        self.campo_ruta.textChanged.connect(self._on_cambio_campos)

        boton_ruta = QPushButton("Seleccionar carpeta…")
        boton_ruta.clicked.connect(self._seleccionar_carpeta)

        self.boton_guardar_preset = QPushButton("Guardar preset")
        self.boton_cargar_preset = QPushButton("Cargar preset")

        layout = QFormLayout(self)
        ruta_layout = QHBoxLayout()
        ruta_layout.addWidget(self.campo_ruta)
        ruta_layout.addWidget(boton_ruta)

        acciones_layout = QHBoxLayout()
        acciones_layout.addWidget(self.boton_guardar_preset)
        acciones_layout.addWidget(self.boton_cargar_preset)

        layout.addRow("Nombre proyecto", self.campo_nombre)
        layout.addRow("Ruta destino", ruta_layout)
        layout.addRow("Descripción", self.campo_descripcion)
        layout.addRow("Versión", self.campo_version)
        layout.addRow("Presets", acciones_layout)

    def _seleccionar_carpeta(self) -> None:
        ruta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de destino")
        if ruta:
            self.campo_ruta.setText(ruta)
            self._on_cambio_campos()

    def _on_cambio_campos(self) -> None:
        estado_actual = self.isComplete()
        if estado_actual != self._estado_complete:
            LOGGER.debug(
                "Completitud en página de datos actualizada: %s -> %s",
                self._estado_complete,
                estado_actual,
            )
            self._estado_complete = estado_actual
        self.completeChanged.emit()

    def isComplete(self) -> bool:  # noqa: N802
        return bool(self.campo_nombre.text().strip()) and bool(self.campo_ruta.text().strip())

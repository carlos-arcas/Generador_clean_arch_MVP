"""Ventana principal de la aplicación de presentación."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow

from presentacion.wizard.wizard_generador import WizardGeneradorProyectos


class VentanaPrincipal(QMainWindow):
    """Contenedor principal que aloja el wizard de generación."""

    def __init__(self, version_generador: str = "") -> None:
        super().__init__()
        self.setWindowTitle("Generador Base Proyectos")
        self.resize(1024, 720)

        self.version_generador = version_generador
        self.wizard = WizardGeneradorProyectos()
        self.setCentralWidget(self.wizard)

"""Ventana principal de la aplicación de presentación."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow

from presentacion.wizard_proyecto import WizardProyecto


class VentanaPrincipal(QMainWindow):
    """Contenedor principal que aloja el wizard de generación."""

    def __init__(self, version_generador: str) -> None:
        super().__init__()
        self.setWindowTitle("Generador Base Proyectos")
        self.resize(1024, 720)

        self.wizard = WizardProyecto(version_generador=version_generador)
        self.setCentralWidget(self.wizard)

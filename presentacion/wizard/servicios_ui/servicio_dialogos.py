"""Servicios auxiliares para diálogos del wizard."""

from __future__ import annotations

from PySide6.QtWidgets import QInputDialog, QMessageBox, QWidget


class ServicioDialogosWizard:
    """Centraliza mensajes y preguntas simples de la UI."""

    def pedir_nombre_preset(self, parent: QWidget) -> tuple[str, bool]:
        return QInputDialog.getText(parent, "Guardar preset", "Nombre del preset")

    def seleccionar_preset(self, parent: QWidget, nombres: list[str]) -> tuple[str, bool]:
        return QInputDialog.getItem(parent, "Cargar preset", "Selecciona un preset", nombres, editable=False)

    def info(self, parent: QWidget, titulo: str, mensaje: str) -> None:
        QMessageBox.information(parent, titulo, mensaje)

    def warning(self, parent: QWidget, titulo: str, mensaje: str) -> None:
        QMessageBox.warning(parent, titulo, mensaje)

    def error(self, parent: QWidget, titulo: str, mensaje: str) -> None:
        QMessageBox.critical(parent, titulo, mensaje)

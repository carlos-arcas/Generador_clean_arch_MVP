"""Servicios auxiliares para mostrar diálogos en UI."""

from __future__ import annotations

from PySide6.QtWidgets import QInputDialog, QMessageBox, QWidget


class ServicioDialogos:
    """Encapsula diálogos de entrada e información de Qt."""

    def pedir_texto(self, parent: QWidget, titulo: str, etiqueta: str) -> tuple[str, bool]:
        return QInputDialog.getText(parent, titulo, etiqueta)

    def pedir_item(self, parent: QWidget, titulo: str, etiqueta: str, opciones: list[str]) -> tuple[str, bool]:
        return QInputDialog.getItem(parent, titulo, etiqueta, opciones, editable=False)

    def informar(self, parent: QWidget, titulo: str, mensaje: str) -> None:
        QMessageBox.information(parent, titulo, mensaje)

    def advertir(self, parent: QWidget, titulo: str, mensaje: str) -> None:
        QMessageBox.warning(parent, titulo, mensaje)

    def error(self, parent: QWidget, titulo: str, mensaje: str) -> None:
        QMessageBox.critical(parent, titulo, mensaje)

"""Página para seleccionar la estrategia de persistencia."""

from __future__ import annotations

from PySide6.QtWidgets import QRadioButton, QVBoxLayout, QWizardPage


class PaginaPersistencia(QWizardPage):
    """Permite seleccionar JSON o SQLite para persistencia inicial."""

    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Persistencia")
        self.setSubTitle("Selecciona el tipo de persistencia inicial.")

        self.radio_json = QRadioButton("JSON")
        self.radio_sqlite = QRadioButton("SQLite")
        self.radio_json.setChecked(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.radio_json)
        layout.addWidget(self.radio_sqlite)

    def persistencia_seleccionada(self) -> str:
        if self.radio_sqlite.isChecked():
            return "SQLite"
        return "JSON"

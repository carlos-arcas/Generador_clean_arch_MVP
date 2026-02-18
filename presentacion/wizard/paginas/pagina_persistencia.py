"""Página para seleccionar la estrategia de persistencia."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QCheckBox,
    QRadioButton,
    QVBoxLayout,
    QWizardPage,
)


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

        self.etiqueta_credenciales = QLabel("Credenciales de conexión (opcional):")
        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Usuario DB/CRM")
        self.campo_password = QLineEdit()
        self.campo_password.setPlaceholderText("Password / token")
        self.campo_password.setEchoMode(QLineEdit.Password)
        self.checkbox_guardar_seguro = QCheckBox("Guardar credencial en sistema seguro")

        layout.addWidget(self.etiqueta_credenciales)
        layout.addWidget(self.campo_usuario)
        layout.addWidget(self.campo_password)
        layout.addWidget(self.checkbox_guardar_seguro)

        self.etiqueta_blueprints = QLabel("Blueprints a aplicar (internos y plugins externos):")
        self.lista_blueprints = QListWidget()
        self.lista_blueprints.setSelectionMode(QAbstractItemView.MultiSelection)

        layout.addWidget(self.etiqueta_blueprints)
        layout.addWidget(self.lista_blueprints)

    def persistencia_seleccionada(self) -> str:
        if self.radio_sqlite.isChecked():
            return "SQLite"
        return "JSON"

    def establecer_persistencia(self, persistencia: str) -> None:
        if persistencia.lower() == "sqlite":
            self.radio_sqlite.setChecked(True)
            return
        self.radio_json.setChecked(True)

    def establecer_blueprints_disponibles(
        self, blueprints: list[tuple[str, str, str]], seleccionados: list[str] | None = None
    ) -> None:
        seleccion = set(seleccionados or [])
        self.lista_blueprints.clear()
        for nombre, version, descripcion in blueprints:
            texto = f"{nombre} ({version}) - {descripcion}"
            item = QListWidgetItem(texto)
            item.setData(256, nombre)
            self.lista_blueprints.addItem(item)
            if nombre in seleccion:
                item.setSelected(True)

    def blueprints_seleccionados(self) -> list[str]:
        return [item.data(256) for item in self.lista_blueprints.selectedItems()]


    def usuario_credencial(self) -> str:
        return self.campo_usuario.text().strip()

    def secreto_credencial(self) -> str:
        return self.campo_password.text()

    def guardar_credencial_segura(self) -> bool:
        return self.checkbox_guardar_seguro.isChecked()

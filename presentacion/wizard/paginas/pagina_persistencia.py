"""Página para seleccionar la estrategia de persistencia."""

from __future__ import annotations

from PySide6.QtCore import Qt
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

from aplicacion.casos_uso.validar_compatibilidad_blueprints import ValidarCompatibilidadBlueprints
from aplicacion.dtos.blueprints import DtoBlueprintMetadata


class PaginaPersistencia(QWizardPage):
    """Permite seleccionar JSON o SQLite para persistencia inicial."""

    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Persistencia")
        self.setSubTitle("Selecciona el tipo de persistencia inicial.")
        self._metadata_blueprints: dict[str, DtoBlueprintMetadata] = {}
        self._validador_compatibilidad = ValidarCompatibilidadBlueprints(self._metadata_blueprints)

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
        self.lista_blueprints.itemSelectionChanged.connect(self._actualizar_estado_compatibilidad)
        self.etiqueta_compatibilidad = QLabel("")

        layout.addWidget(self.etiqueta_blueprints)
        layout.addWidget(self.lista_blueprints)
        layout.addWidget(self.etiqueta_compatibilidad)

    def persistencia_seleccionada(self) -> str:
        if self.radio_sqlite.isChecked():
            return "SQLite"
        return "JSON"

    def establecer_persistencia(self, persistencia: str) -> None:
        if persistencia.lower() == "sqlite":
            self.radio_sqlite.setChecked(True)
            return
        self.radio_json.setChecked(True)

    def establecer_metadata_blueprints(self, metadata_blueprints: dict[str, DtoBlueprintMetadata]) -> None:
        self._metadata_blueprints = metadata_blueprints
        self._validador_compatibilidad = ValidarCompatibilidadBlueprints(self._metadata_blueprints)

    def establecer_blueprints_disponibles(
        self, blueprints: list[tuple[str, str, str]], seleccionados: list[str] | None = None
    ) -> None:
        seleccion = set(seleccionados or [])
        self.lista_blueprints.clear()
        for nombre, version, descripcion in blueprints:
            metadata = self._metadata_blueprints.get(nombre)
            texto = self._descripcion_blueprint(nombre, version, descripcion, metadata)
            item = QListWidgetItem(texto)
            item.setData(256, nombre)
            self.lista_blueprints.addItem(item)
            if nombre in seleccion:
                item.setSelected(True)
        self._actualizar_estado_compatibilidad()

    def blueprints_seleccionados(self) -> list[str]:
        return [item.data(256) for item in self.lista_blueprints.selectedItems()]

    def usuario_credencial(self) -> str:
        return self.campo_usuario.text().strip()

    def secreto_credencial(self) -> str:
        return self.campo_password.text()

    def guardar_credencial_segura(self) -> bool:
        return self.checkbox_guardar_seguro.isChecked()

    def _descripcion_blueprint(
        self,
        nombre: str,
        version: str,
        descripcion: str,
        metadata: DtoBlueprintMetadata | None,
    ) -> str:
        if metadata is None:
            return f"{nombre} ({version}) - {descripcion}"
        capas = ", ".join(metadata.genera_capas) if metadata.genera_capas else "N/D"
        requiere_clases = "Sí" if metadata.requiere_clases else "No"
        return (
            f"{nombre} ({version}) - {metadata.descripcion or descripcion} | "
            f"Tipo: {metadata.tipo} | Capas: {capas} | Requiere clases: {requiere_clases}"
        )

    def _actualizar_estado_compatibilidad(self) -> None:
        seleccionados = self.blueprints_seleccionados()
        incompatibles = self._calcular_incompatibles(seleccionados)

        for indice in range(self.lista_blueprints.count()):
            item = self.lista_blueprints.item(indice)
            nombre = item.data(256)
            deshabilitado = nombre in incompatibles and nombre not in seleccionados
            if deshabilitado:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                continue
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)

        if incompatibles:
            self.etiqueta_compatibilidad.setText(
                f"Advertencia: hay incompatibilidades declarativas. Deshabilitados: {', '.join(sorted(incompatibles))}."
            )
            return

        self.etiqueta_compatibilidad.setText("")

    def _calcular_incompatibles(self, seleccionados: list[str]) -> set[str]:
        incompatibles: set[str] = set()
        todos = [self.lista_blueprints.item(i).data(256) for i in range(self.lista_blueprints.count())]
        for candidato in todos:
            if candidato in seleccionados:
                continue
            resultado = self._validador_compatibilidad.ejecutar([*seleccionados, candidato], hay_clases=True)
            if not resultado.es_valido:
                incompatibles.add(candidato)
        return incompatibles

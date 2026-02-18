"""Página de resumen final de configuración del wizard."""

from __future__ import annotations

from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWizardPage


class PaginaResumen(QWizardPage):
    """Renderiza un resumen textual de la configuración actual."""

    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Resumen")
        self.setSubTitle("Verifica la configuración antes de finalizar.")

        self._texto_resumen = QTextEdit()
        self._texto_resumen.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self._texto_resumen)

    def initializePage(self) -> None:  # noqa: N802
        wizard = self.wizard()
        if wizard is None:
            self._texto_resumen.clear()
            return

        texto = self.construir_resumen(
            nombre=wizard.pagina_datos.campo_nombre.text().strip(),
            ruta=wizard.pagina_datos.campo_ruta.text().strip(),
            descripcion=wizard.pagina_datos.campo_descripcion.text().strip(),
            version=wizard.pagina_datos.campo_version.text().strip(),
            clases=wizard.pagina_clases.clases(),
            persistencia=wizard.pagina_persistencia.persistencia_seleccionada(),
        )
        self._texto_resumen.setPlainText(texto)

    def construir_resumen(
        self,
        *,
        nombre: str,
        ruta: str,
        descripcion: str,
        version: str,
        clases: list[str],
        persistencia: str,
    ) -> str:
        listado_clases = "\n".join(f"- {clase}" for clase in clases) or "- (sin clases)"
        return (
            f"Nombre proyecto: {nombre}\n"
            f"Ruta destino: {ruta}\n"
            f"Descripción: {descripcion}\n"
            f"Versión: {version}\n"
            f"Persistencia: {persistencia}\n"
            "Clases:\n"
            f"{listado_clases}"
        )

    def texto_resumen(self) -> str:
        return self._texto_resumen.toPlainText()

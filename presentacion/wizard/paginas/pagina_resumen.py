"""Página de resumen final de configuración del wizard."""

from __future__ import annotations

from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWizardPage

from dominio.modelos import EspecificacionProyecto


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
            especificacion_proyecto=wizard.especificacion_proyecto,
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
        especificacion_proyecto: EspecificacionProyecto,
        persistencia: str,
    ) -> str:
        listado_clases = self._construir_bloque_clases(especificacion_proyecto)
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

    def _construir_bloque_clases(self, especificacion_proyecto: EspecificacionProyecto) -> str:
        if not especificacion_proyecto.clases:
            return "- (sin clases)"

        bloques: list[str] = []
        for clase in especificacion_proyecto.clases:
            bloques.append(f"Clase: {clase.nombre}")
            if not clase.atributos:
                bloques.append("  - (sin atributos)")
                continue

            for atributo in clase.atributos:
                texto = f"  - {atributo.nombre}: {atributo.tipo}"
                if atributo.obligatorio:
                    texto += " (obligatorio)"
                bloques.append(texto)

        return "\n".join(bloques)

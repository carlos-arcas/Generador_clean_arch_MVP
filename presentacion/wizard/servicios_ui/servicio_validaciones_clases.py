"""Servicios auxiliares para validaciones y acceso de página de clases."""

from __future__ import annotations

from PySide6.QtWidgets import QWizard

from dominio.modelos import EspecificacionClase, EspecificacionProyecto


class ServicioValidacionesClases:
    """Encapsula utilidades no visuales usadas en la página de clases."""

    def normalizar_nombre(self, nombre: str) -> str | None:
        nombre_limpio = nombre.strip()
        if not nombre_limpio:
            return None
        return nombre_limpio

    def obtener_especificacion(self, wizard: object) -> EspecificacionProyecto:
        if wizard is None or not isinstance(wizard, QWizard):
            raise RuntimeError("La página de clases requiere estar asociada a un QWizard.")
        especificacion = getattr(wizard, "especificacion_proyecto", None)
        if not isinstance(especificacion, EspecificacionProyecto):
            raise RuntimeError("El wizard no contiene una especificación de proyecto válida.")
        return especificacion

    def clase_seleccionada(self, wizard: object, indice: int) -> EspecificacionClase | None:
        clases = self.obtener_especificacion(wizard).clases
        if indice < 0 or indice >= len(clases):
            return None
        return clases[indice]

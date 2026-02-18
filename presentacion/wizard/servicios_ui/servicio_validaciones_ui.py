"""Validaciones visuales reutilizables del wizard."""

from __future__ import annotations


class ServicioValidacionesUi:
    """Valida datos capturados desde controles de UI."""

    def validar_nombre_no_vacio(self, texto: str) -> bool:
        return bool(texto.strip())

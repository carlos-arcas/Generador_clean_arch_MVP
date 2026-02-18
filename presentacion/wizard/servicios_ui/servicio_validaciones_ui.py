"""Validaciones visuales para formularios del wizard."""

from __future__ import annotations

from collections.abc import Iterable


class ServicioValidacionesUi:
    """Aplica validaciones simples para entradas de UI."""

    def normalizar_nombre(self, valor: str) -> str | None:
        nombre = valor.strip()
        if not nombre:
            return None
        return nombre

    def esta_duplicado(self, nombre: str, existentes: Iterable[str]) -> bool:
        return any(existente == nombre for existente in existentes)

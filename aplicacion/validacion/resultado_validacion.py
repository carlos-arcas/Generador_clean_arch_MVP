"""Resultado estándar para reglas de validación."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoValidacion:
    """Representa el resultado de una validación puntual."""

    exito: bool
    mensaje: str | None
    severidad: str


"""Contrato para reglas de validación reutilizables."""

from __future__ import annotations

from aplicacion.validacion.resultado_validacion import ResultadoValidacion


class ReglaValidacion:
    """Define una regla de validación ejecutable sobre un contexto."""

    def validar(self, contexto: object) -> ResultadoValidacion | None:
        raise NotImplementedError


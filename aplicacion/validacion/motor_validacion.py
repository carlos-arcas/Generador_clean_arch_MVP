"""Motor de ejecución para reglas de validación."""

from __future__ import annotations

from aplicacion.validacion.regla_validacion import ReglaValidacion
from aplicacion.validacion.resultado_validacion import ResultadoValidacion


class MotorValidacion:
    """Ejecuta una secuencia de reglas sobre un contexto."""

    def __init__(self, reglas: list[ReglaValidacion]) -> None:
        self._reglas = reglas

    def ejecutar(self, contexto: object) -> list[ResultadoValidacion]:
        resultados: list[ResultadoValidacion] = []
        for regla in self._reglas:
            resultado = regla.validar(contexto)
            if resultado is not None:
                resultados.append(resultado)
        return resultados


from __future__ import annotations

from aplicacion.validacion.motor_validacion import MotorValidacion
from aplicacion.validacion.regla_validacion import ReglaValidacion
from aplicacion.validacion.resultado_validacion import ResultadoValidacion


class _ReglaLongitudMinima(ReglaValidacion):
    def validar(self, contexto: object) -> ResultadoValidacion | None:
        texto = str(contexto)
        if len(texto) < 3:
            return ResultadoValidacion(exito=False, mensaje="mínimo 3 caracteres", severidad="ERROR")
        return ResultadoValidacion(exito=True, mensaje=None, severidad="INFO")


def test_motor_validacion_evalua_regla_y_devuelve_resultado() -> None:
    motor = MotorValidacion([_ReglaLongitudMinima()])

    resultado_error = motor.ejecutar("ab")
    resultado_ok = motor.ejecutar("abcd")

    assert resultado_error[0].exito is False
    assert resultado_error[0].mensaje == "mínimo 3 caracteres"
    assert resultado_ok[0] == ResultadoValidacion(exito=True, mensaje=None, severidad="INFO")

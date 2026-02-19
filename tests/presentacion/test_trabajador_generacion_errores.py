"""Pruebas de manejo de errores tipados del trabajador de generación."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import Any

import pytest

from aplicacion.errores import ErrorAplicacion
from presentacion.mapeo_mensajes_error import MensajeUxError
from presentacion.trabajadores.trabajador_generacion import TrabajadorGeneracionMvp


@dataclass
class _Canal:
    eventos: list[tuple[Any, ...]] = field(default_factory=list)

    def emit(self, *args: Any) -> None:
        self.eventos.append(args)


class _SenalesFalsas:
    def __init__(self) -> None:
        self.progreso = _Canal()
        self.exito = _Canal()
        self.error = _Canal()


class _CasoUsoFalla:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def ejecutar(self, _entrada: object) -> object:
        raise self._error


def _crear_trabajador(error: Exception) -> tuple[TrabajadorGeneracionMvp, _SenalesFalsas]:
    trabajador = TrabajadorGeneracionMvp(caso_uso=_CasoUsoFalla(error), entrada=object())
    senales = _SenalesFalsas()
    trabajador.senales = senales
    return trabajador, senales


def test_error_aplicacion_emite_error_y_loguea_stacktrace(caplog: pytest.LogCaptureFixture) -> None:
    trabajador, senales = _crear_trabajador(ErrorAplicacion("fallo de dominio"))

    with caplog.at_level("ERROR"):
        trabajador.run()

    assert senales.error.eventos
    (mensaje_ux,) = senales.error.eventos[0]
    assert isinstance(mensaje_ux, MensajeUxError)
    assert "ID de incidente" in mensaje_ux.mensaje
    assert "falló mvp" not in mensaje_ux.mensaje.lower()
    assert "id_incidente=" in caplog.text
    assert any(registro.exc_info for registro in caplog.records)


def test_oserror_emite_error_generico_y_loguea_stacktrace(caplog: pytest.LogCaptureFixture) -> None:
    trabajador, senales = _crear_trabajador(OSError("sin permisos"))

    with caplog.at_level("ERROR"):
        trabajador.run()

    assert senales.error.eventos
    (mensaje_ux,) = senales.error.eventos[0]
    assert isinstance(mensaje_ux, MensajeUxError)
    assert mensaje_ux.causa_probable is not None
    assert mensaje_ux.acciones
    assert "id_incidente=" in caplog.text
    assert any(registro.exc_info for registro in caplog.records)


def test_no_quedan_except_exception_en_trabajadores() -> None:
    resultado = subprocess.run(
        ["rg", "-n", "except Exception", "presentacion/trabajadores"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 1, resultado.stdout

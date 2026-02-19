"""Pruebas unitarias para el mapeo de mensajes de error del wizard."""

from __future__ import annotations

import inspect

from aplicacion.errores import ErrorGeneracionProyecto, ErrorValidacionEntrada
from presentacion.wizard.orquestadores import orquestador_finalizacion_wizard as modulo


class ErrorDesconocido(Exception):
    """Error ad-hoc para validar fallback de mapeo."""


def _crear_orquestador() -> modulo.OrquestadorFinalizacionWizard:
    return modulo.OrquestadorFinalizacionWizard(
        validador_final=lambda proyecto: proyecto,
        lanzador_generacion=lambda entrada: None,
    )


def test_mapear_mensaje_error_validacion() -> None:
    orquestador = _crear_orquestador()

    mensaje = orquestador._mapear_mensaje_error(ErrorValidacionEntrada("faltan datos"))

    assert mensaje == "Error de validación: faltan datos"


def test_mapear_mensaje_error_generacion() -> None:
    orquestador = _crear_orquestador()

    mensaje = orquestador._mapear_mensaje_error(ErrorGeneracionProyecto("falló pipeline"))

    assert mensaje == "Error al iniciar generación: falló pipeline"


def test_mapear_mensaje_error_oserror() -> None:
    orquestador = _crear_orquestador()

    mensaje = orquestador._mapear_mensaje_error(OSError("sin permisos"))

    assert mensaje == "Error técnico al iniciar generación."


def test_mapear_mensaje_error_desconocido() -> None:
    orquestador = _crear_orquestador()

    mensaje = orquestador._mapear_mensaje_error(ErrorDesconocido("sin mapeo"))

    assert mensaje == "Error técnico al iniciar generación."


def test_mapear_mensaje_error_complejidad_reducida() -> None:
    codigo = inspect.getsource(modulo.OrquestadorFinalizacionWizard._mapear_mensaje_error)

    assert "MAPEO_ERRORES_A_MENSAJES" in codigo
    assert codigo.count("if isinstance") == 1

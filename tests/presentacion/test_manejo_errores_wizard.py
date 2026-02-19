"""Pruebas de manejo de errores tipados en wizard y orquestador."""

from __future__ import annotations

import subprocess

import pytest

from aplicacion.errores import ErrorInfraestructura, ErrorValidacionEntrada
from aplicacion.dtos.proyecto import DtoProyectoEntrada
from presentacion.wizard.dtos import DatosWizardProyecto
from presentacion.wizard.orquestadores.orquestador_finalizacion_wizard import (
    DtoEntradaFinalizacionWizard,
    OrquestadorFinalizacionWizard,
)


def _datos_wizard(
    *,
    guardar_credencial: bool = False,
    usuario_credencial: str = "",
    secreto_credencial: str = "",
) -> DatosWizardProyecto:
    proyecto = DtoProyectoEntrada(nombre_proyecto="Demo", ruta_destino="/tmp/demo")
    return DatosWizardProyecto(
        nombre="Demo",
        ruta="/tmp/demo",
        descripcion="",
        version="0.1.0",
        proyecto=proyecto,
        persistencia="JSON",
        usuario_credencial=usuario_credencial,
        secreto_credencial=secreto_credencial,
        guardar_credencial=guardar_credencial,
    )


def test_error_validacion_devuelve_mensaje_controlado() -> None:
    def _validador(_proyecto: DtoProyectoEntrada) -> object:
        raise ErrorValidacionEntrada("Datos inválidos para el proyecto")

    orquestador = OrquestadorFinalizacionWizard(
        validador_final=_validador,
        lanzador_generacion=lambda _entrada: None,
    )

    resultado = orquestador.finalizar(
        DtoEntradaFinalizacionWizard(datos_wizard=_datos_wizard(), blueprints=["base_clean_arch"])
    )

    assert resultado.exito is False
    assert resultado.mensaje_usuario == "Error de validación: Datos inválidos para el proyecto"


def test_error_infraestructura_credenciales_genera_advertencia_y_log(caplog: pytest.LogCaptureFixture) -> None:
    class ServicioCredencialesFalla:
        def ejecutar_desde_datos(self, **_kwargs: str) -> None:
            raise ErrorInfraestructura("Fallo en almacenamiento seguro")

    datos = _datos_wizard(
        guardar_credencial=True,
        usuario_credencial="usuario",
        secreto_credencial="secreto",
    )

    orquestador = OrquestadorFinalizacionWizard(
        validador_final=lambda proyecto: proyecto,
        lanzador_generacion=lambda _entrada: None,
        servicio_credenciales=ServicioCredencialesFalla(),
    )

    with caplog.at_level("WARNING"):
        resultado = orquestador.finalizar(
            DtoEntradaFinalizacionWizard(datos_wizard=datos, blueprints=["base_clean_arch"])
        )

    assert resultado.exito is True
    assert "advertencia_credenciales" in (resultado.detalles or {})
    assert "No se pudo persistir credencial" in caplog.text


def test_no_quedan_except_exception_en_wizard_e_infraestructura_seguridad() -> None:
    resultado = subprocess.run(
        ["rg", "-n", "except Exception", "presentacion/wizard", "infraestructura/seguridad"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 1, resultado.stdout

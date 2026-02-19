"""Pruebas de refactor para finalización del wizard."""

from __future__ import annotations

import inspect

from aplicacion.dtos.proyecto import DtoProyectoEntrada
from aplicacion.errores import ErrorAplicacion, ErrorInfraestructura
from presentacion.wizard.dtos import DatosWizardProyecto
from presentacion.wizard.orquestadores.orquestador_finalizacion_wizard import (
    DtoEntradaFinalizacionWizard,
    OrquestadorFinalizacionWizard,
)


class _CredencialesFalla:
    def ejecutar_desde_datos(self, **_kwargs: object) -> None:
        raise ValueError("almacén seguro no disponible")


class _CredencialesOk:
    def __init__(self) -> None:
        self.ejecutado = False

    def ejecutar_desde_datos(self, **_kwargs: object) -> None:
        self.ejecutado = True


def _crear_datos_wizard(
    nombre: str = "MiProyecto",
    ruta: str = "/tmp/proyecto",
    persistencia: str = "JSON",
    guardar_credencial: bool = False,
    usuario_credencial: str = "",
    secreto_credencial: str = "",
) -> DatosWizardProyecto:
    proyecto = DtoProyectoEntrada(nombre_proyecto=nombre, ruta_destino=ruta)
    return DatosWizardProyecto(
        nombre=nombre,
        ruta=ruta,
        descripcion="",
        version="0.1.0",
        proyecto=proyecto,
        persistencia=persistencia,
        usuario_credencial=usuario_credencial,
        secreto_credencial=secreto_credencial,
        guardar_credencial=guardar_credencial,
    )


def test_finalizar_happy_path_devuelve_resultado_exitoso() -> None:
    lanzamientos: list[object] = []
    orquestador = OrquestadorFinalizacionWizard(
        validador_final=lambda proyecto: proyecto,
        lanzador_generacion=lambda entrada: lanzamientos.append(entrada),
    )

    resultado = orquestador.finalizar(
        DtoEntradaFinalizacionWizard(
            datos_wizard=_crear_datos_wizard(),
            blueprints=["base_clean_arch"],
        )
    )

    assert resultado.exito is True
    assert resultado.mensaje_usuario == "Generación iniciada."
    assert resultado.detalles == {"generacion_iniciada": True}
    assert len(lanzamientos) == 1


def test_finalizar_error_validacion_devuelve_error_controlado() -> None:
    def _falla_validacion(_proyecto: DtoProyectoEntrada) -> DtoProyectoEntrada:
        raise ValueError("Nombre de proyecto inválido")

    orquestador = OrquestadorFinalizacionWizard(
        validador_final=_falla_validacion,
        lanzador_generacion=lambda _entrada: None,
    )

    resultado = orquestador.finalizar(
        DtoEntradaFinalizacionWizard(
            datos_wizard=_crear_datos_wizard(nombre=""),
            blueprints=["base_clean_arch"],
        )
    )

    assert resultado.exito is False
    assert "Error de validación" in resultado.mensaje_usuario
    assert "inválido" in resultado.mensaje_usuario


def test_finalizar_error_tecnico_devuelve_error_controlado() -> None:
    def _falla_generacion(_entrada: object) -> None:
        raise ErrorInfraestructura("falló filesystem")

    orquestador = OrquestadorFinalizacionWizard(
        validador_final=lambda proyecto: proyecto,
        lanzador_generacion=_falla_generacion,
    )

    resultado = orquestador.finalizar(
        DtoEntradaFinalizacionWizard(
            datos_wizard=_crear_datos_wizard(),
            blueprints=["base_clean_arch"],
        )
    )

    assert resultado.exito is False
    assert resultado.mensaje_usuario == "Error técnico al iniciar generación."


def test_finalizar_maneja_advertencia_credenciales_y_presets() -> None:
    orquestador = OrquestadorFinalizacionWizard(
        validador_final=lambda proyecto: proyecto,
        lanzador_generacion=lambda _entrada: None,
        servicio_credenciales=_CredencialesFalla(),
        servicio_presets=object(),
    )

    resultado = orquestador.finalizar(
        DtoEntradaFinalizacionWizard(
            datos_wizard=_crear_datos_wizard(
                guardar_credencial=True,
                usuario_credencial="admin",
                secreto_credencial="secreto",
            ),
            blueprints=["base_clean_arch"],
        )
    )

    assert resultado.exito is True
    assert resultado.detalles == {
        "presets_disponibles": True,
        "advertencia_credenciales": (
            "No se pudo guardar la credencial en el sistema seguro. "
            "Se usará únicamente en memoria durante esta ejecución."
        ),
        "generacion_iniciada": True,
    }


def test_finalizar_guardado_credenciales_exitoso() -> None:
    credenciales = _CredencialesOk()
    orquestador = OrquestadorFinalizacionWizard(
        validador_final=lambda proyecto: proyecto,
        lanzador_generacion=lambda _entrada: None,
        servicio_credenciales=credenciales,
    )

    resultado = orquestador.finalizar(
        DtoEntradaFinalizacionWizard(
            datos_wizard=_crear_datos_wizard(
                guardar_credencial=True,
                usuario_credencial="admin",
                secreto_credencial="secreto",
            ),
            blueprints=[],
        )
    )

    assert credenciales.ejecutado is True
    assert resultado.detalles == {"credencial_guardada": True, "generacion_iniciada": True}


def test_finalizar_error_aplicacion_controlado() -> None:
    def _falla_generacion(_entrada: object) -> None:
        raise ErrorAplicacion("regla de negocio inválida")

    orquestador = OrquestadorFinalizacionWizard(
        validador_final=lambda proyecto: proyecto,
        lanzador_generacion=_falla_generacion,
    )

    resultado = orquestador.finalizar(
        DtoEntradaFinalizacionWizard(datos_wizard=_crear_datos_wizard(), blueprints=[])
    )

    assert resultado.exito is False
    assert "Error al iniciar generación" in resultado.mensaje_usuario


def test_finalizar_tiene_menos_de_50_lineas() -> None:
    codigo = inspect.getsource(OrquestadorFinalizacionWizard.finalizar)
    lineas_funcionales = [
        linea
        for linea in codigo.splitlines()
        if linea.strip() and not linea.strip().startswith("#")
    ]

    assert len(lineas_funcionales) < 50

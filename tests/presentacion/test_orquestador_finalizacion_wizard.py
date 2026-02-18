"""Pruebas unitarias para el orquestador de finalización del wizard."""

from __future__ import annotations

from aplicacion.dtos.proyecto import DtoProyectoEntrada
from presentacion.wizard.dtos import DatosWizardProyecto
from presentacion.wizard.orquestadores.orquestador_finalizacion_wizard import (
    DtoEntradaFinalizacionWizard,
    OrquestadorFinalizacionWizard,
)


class CredencialesFalsa:
    def __init__(self) -> None:
        self.llamadas: list[dict[str, str]] = []

    def ejecutar_desde_datos(
        self,
        identificador: str,
        usuario: str,
        secreto: str,
        tipo: str,
    ) -> None:
        self.llamadas.append(
            {
                "identificador": identificador,
                "usuario": usuario,
                "secreto": secreto,
                "tipo": tipo,
            }
        )


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


def test_finalizar_ok_devuelve_exito_y_lanza_generacion() -> None:
    lanzamientos: list[object] = []
    credenciales = CredencialesFalsa()

    orquestador = OrquestadorFinalizacionWizard(
        validador_final=lambda proyecto: proyecto,
        lanzador_generacion=lambda entrada: lanzamientos.append(entrada),
        servicio_credenciales=credenciales,
    )

    datos = _crear_datos_wizard(
        guardar_credencial=True,
        usuario_credencial="admin",
        secreto_credencial="secreto",
    )
    resultado = orquestador.finalizar(
        DtoEntradaFinalizacionWizard(datos_wizard=datos, blueprints=["base_clean_arch", "crud_json"])
    )

    assert resultado.exito is True
    assert resultado.mensaje_usuario == "Generación iniciada."
    assert len(lanzamientos) == 1
    assert resultado.detalles == {"credencial_guardada": True, "generacion_iniciada": True}
    assert credenciales.llamadas[0]["identificador"] == "generador:MiProyecto:json"


def test_finalizar_error_validacion_devuelve_error_y_no_lanza_generacion() -> None:
    lanzamientos: list[object] = []

    def _fallar_validacion(proyecto):  # noqa: ANN001
        raise ValueError(f"Nombre inválido: {proyecto.nombre_proyecto}")

    orquestador = OrquestadorFinalizacionWizard(
        validador_final=_fallar_validacion,
        lanzador_generacion=lambda entrada: lanzamientos.append(entrada),
    )

    datos = _crear_datos_wizard(nombre="")
    resultado = orquestador.finalizar(
        DtoEntradaFinalizacionWizard(datos_wizard=datos, blueprints=["base_clean_arch"])
    )

    assert resultado.exito is False
    assert "Error de validación" in resultado.mensaje_usuario
    assert "Nombre inválido" in resultado.mensaje_usuario
    assert lanzamientos == []


def test_finalizar_entrada_minima_sin_preset_ni_credenciales() -> None:
    lanzamientos: list[object] = []

    orquestador = OrquestadorFinalizacionWizard(
        validador_final=lambda proyecto: proyecto,
        lanzador_generacion=lambda entrada: lanzamientos.append(entrada),
    )

    datos = _crear_datos_wizard(nombre="Minimo", ruta="/tmp/minimo")
    resultado = orquestador.finalizar(
        DtoEntradaFinalizacionWizard(datos_wizard=datos, blueprints=[])
    )

    assert resultado.exito is True
    assert resultado.detalles == {"generacion_iniciada": True}
    assert len(lanzamientos) == 1
    assert lanzamientos[0].blueprints == []

"""Pruebas de validaciones del caso de uso ConstruirEspecificacionProyecto."""

from __future__ import annotations

import pytest

from aplicacion.casos_uso.construir_especificacion_proyecto import ConstruirEspecificacionProyecto
from aplicacion.dtos.proyecto import DtoAtributo, DtoClase, DtoProyectoEntrada
from aplicacion.errores import ErrorValidacion


def _crear_dto_base() -> DtoProyectoEntrada:
    return DtoProyectoEntrada(
        nombre_proyecto="Inventario",
        ruta_destino="/tmp/inventario",
        version="1.0.0",
        clases=[
            DtoClase(
                nombre="Producto",
                atributos=[DtoAtributo(nombre="id", tipo="int", obligatorio=True)],
            )
        ],
    )


def test_dto_valido_pasa_sin_excepcion() -> None:
    caso_uso = ConstruirEspecificacionProyecto()

    especificacion = caso_uso.ejecutar(_crear_dto_base())

    assert especificacion.nombre_proyecto == "Inventario"


def test_nombre_vacio_lanza_error_validacion() -> None:
    caso_uso = ConstruirEspecificacionProyecto()
    dto = DtoProyectoEntrada(
        nombre_proyecto="   ",
        ruta_destino="/tmp/inventario",
        clases=[DtoClase(nombre="Producto", atributos=[DtoAtributo(nombre="id", tipo="int")])],
    )

    with pytest.raises(ErrorValidacion, match="nombre del proyecto"):
        caso_uso.ejecutar(dto)


def test_clases_duplicadas_lanzan_excepcion() -> None:
    caso_uso = ConstruirEspecificacionProyecto()
    dto = DtoProyectoEntrada(
        nombre_proyecto="Inventario",
        ruta_destino="/tmp/inventario",
        clases=[
            DtoClase(nombre="Producto", atributos=[DtoAtributo(nombre="id", tipo="int")]),
            DtoClase(nombre="Producto", atributos=[DtoAtributo(nombre="sku", tipo="str")]),
        ],
    )

    with pytest.raises(ErrorValidacion, match="clases duplicadas"):
        caso_uso.ejecutar(dto)


def test_atributo_invalido_lanza_excepcion() -> None:
    caso_uso = ConstruirEspecificacionProyecto()
    dto = DtoProyectoEntrada(
        nombre_proyecto="Inventario",
        ruta_destino="/tmp/inventario",
        clases=[
            DtoClase(
                nombre="Producto",
                atributos=[DtoAtributo(nombre="   ", tipo="int", obligatorio=True)],
            )
        ],
    )

    with pytest.raises(ErrorValidacion, match="nombre del atributo"):
        caso_uso.ejecutar(dto)


def test_caso_limite_sin_clases_es_comportamiento_permitido() -> None:
    caso_uso = ConstruirEspecificacionProyecto()
    dto = DtoProyectoEntrada(
        nombre_proyecto="Inventario",
        ruta_destino="/tmp/inventario",
        clases=[],
    )

    especificacion = caso_uso.ejecutar(dto)

    assert especificacion.clases == []

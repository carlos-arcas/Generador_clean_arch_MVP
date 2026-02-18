"""Pruebas del caso de uso para construir especificación de proyecto."""

from __future__ import annotations

import pytest

from aplicacion.casos_uso.construir_especificacion_proyecto import ConstruirEspecificacionProyecto
from aplicacion.dtos.proyecto import DtoAtributo, DtoClase, DtoProyectoEntrada
from aplicacion.errores import ErrorValidacion



def test_construye_especificacion_valida() -> None:
    caso_uso = ConstruirEspecificacionProyecto()
    dto = DtoProyectoEntrada(
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

    especificacion = caso_uso.ejecutar(dto)

    assert especificacion.nombre_proyecto == "Inventario"
    assert len(especificacion.clases) == 1
    assert especificacion.clases[0].atributos[0].nombre == "id"


def test_falla_si_nombre_proyecto_vacio() -> None:
    caso_uso = ConstruirEspecificacionProyecto()
    dto = DtoProyectoEntrada(
        nombre_proyecto="   ",
        ruta_destino="/tmp/inventario",
        clases=[DtoClase(nombre="Producto", atributos=[DtoAtributo(nombre="id", tipo="int")])],
    )

    with pytest.raises(ErrorValidacion, match="nombre del proyecto"):
        caso_uso.ejecutar(dto)


def test_falla_si_clase_no_tiene_atributos() -> None:
    caso_uso = ConstruirEspecificacionProyecto()
    dto = DtoProyectoEntrada(
        nombre_proyecto="Inventario",
        ruta_destino="/tmp/inventario",
        clases=[DtoClase(nombre="Producto", atributos=[])],
    )

    with pytest.raises(ErrorValidacion, match="debe tener al menos un atributo"):
        caso_uso.ejecutar(dto)


def test_falla_si_tipo_atributo_invalido() -> None:
    caso_uso = ConstruirEspecificacionProyecto()
    dto = DtoProyectoEntrada(
        nombre_proyecto="Inventario",
        ruta_destino="/tmp/inventario",
        clases=[DtoClase(nombre="Producto", atributos=[DtoAtributo(nombre="fecha", tipo="date")])],
    )

    with pytest.raises(ErrorValidacion, match="no es válido"):
        caso_uso.ejecutar(dto)

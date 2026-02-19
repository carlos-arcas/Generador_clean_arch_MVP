"""Pruebas del mapeador de presentación entre dominio y DTOs de vista."""

from __future__ import annotations

import ast
from pathlib import Path

from dominio.especificacion import EspecificacionAtributo, EspecificacionClase
from presentacion.dtos import DtoVistaAtributo, DtoVistaClase
from presentacion.mapeadores.mapeador_dominio_a_vista import (
    mapear_clase_dominio_a_dto_vista,
    mapear_dto_vista_a_clase_dominio,
)


def test_mapear_clase_dominio_a_dto_vista() -> None:
    clase_dominio = EspecificacionClase(
        nombre="Cliente",
        atributos=[
            EspecificacionAtributo(
                nombre="edad",
                tipo="int",
                obligatorio=False,
                valor_por_defecto="18",
            )
        ],
    )

    dto = mapear_clase_dominio_a_dto_vista(clase_dominio)

    assert dto == DtoVistaClase(
        nombre="Cliente",
        atributos=[
            DtoVistaAtributo(
                nombre="edad",
                tipo="int",
                obligatorio=False,
                valor_por_defecto="18",
            )
        ],
    )


def test_mapear_dto_vista_a_clase_dominio() -> None:
    dto = DtoVistaClase(
        nombre="Pedido",
        atributos=[
            DtoVistaAtributo(
                nombre="total",
                tipo="float",
                obligatorio=True,
                valor_por_defecto="",
            )
        ],
    )

    clase_dominio = mapear_dto_vista_a_clase_dominio(dto)

    assert clase_dominio.nombre == "Pedido"
    assert len(clase_dominio.atributos) == 1
    atributo = clase_dominio.atributos[0]
    assert atributo.nombre == "total"
    assert atributo.tipo == "float"
    assert atributo.obligatorio is True
    assert atributo.valor_por_defecto is None


def test_aplicacion_no_contiene_modulos_dtos_presentacion_ni_mapeador_presentacion() -> None:
    assert not Path("aplicacion/dtos_presentacion").exists()
    assert not Path("aplicacion/mapeadores/mapeador_dominio_a_presentacion.py").exists()


def test_aplicacion_no_importa_presentacion_por_ast() -> None:
    for archivo in Path("aplicacion").rglob("*.py"):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    assert not alias.name.startswith("presentacion")
            if isinstance(nodo, ast.ImportFrom):
                modulo = nodo.module or ""
                assert not modulo.startswith("presentacion")

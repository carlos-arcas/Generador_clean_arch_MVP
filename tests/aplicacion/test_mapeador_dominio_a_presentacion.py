"""Pruebas del mapeador de aplicación entre dominio y DTOs de presentación."""

from __future__ import annotations

import ast
from pathlib import Path

from aplicacion.dtos_presentacion import DtoAtributoPresentacion, DtoClasePresentacion
from aplicacion.mapeadores.mapeador_dominio_a_presentacion import (
    mapear_clase_dominio_a_dto,
    mapear_dto_a_clase_dominio,
)
from dominio.especificacion import EspecificacionAtributo, EspecificacionClase


def test_mapear_clase_dominio_a_dto() -> None:
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

    dto = mapear_clase_dominio_a_dto(clase_dominio)

    assert dto == DtoClasePresentacion(
        nombre="Cliente",
        atributos=[
            DtoAtributoPresentacion(
                nombre="edad",
                tipo="int",
                obligatorio=False,
                valor_por_defecto="18",
            )
        ],
    )


def test_mapear_dto_a_clase_dominio() -> None:
    dto = DtoClasePresentacion(
        nombre="Pedido",
        atributos=[
            DtoAtributoPresentacion(
                nombre="total",
                tipo="float",
                obligatorio=True,
                valor_por_defecto="",
            )
        ],
    )

    clase_dominio = mapear_dto_a_clase_dominio(dto)

    assert clase_dominio.nombre == "Pedido"
    assert len(clase_dominio.atributos) == 1
    atributo = clase_dominio.atributos[0]
    assert atributo.nombre == "total"
    assert atributo.tipo == "float"
    assert atributo.obligatorio is True
    assert atributo.valor_por_defecto is None


def test_presentacion_no_importa_dominio() -> None:
    ruta_presentacion = Path("presentacion")
    for archivo in ruta_presentacion.rglob("*.py"):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    assert not alias.name.startswith("dominio")
            if isinstance(nodo, ast.ImportFrom):
                modulo = nodo.module or ""
                assert not modulo.startswith("dominio")


def test_archivo_mapper_en_presentacion_no_existe() -> None:
    assert not Path("presentacion/mappers/mapper_dominio_a_presentacion.py").exists()

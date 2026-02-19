"""Validaciones de desacoplamiento de modelos Qt respecto al dominio."""

from __future__ import annotations

from pathlib import Path

from dominio.especificacion import EspecificacionAtributo, EspecificacionClase
from presentacion.dtos import DtoVistaAtributo, DtoVistaClase
from presentacion.mapeadores.mapeador_dominio_a_vista import (
    mapear_clase_dominio_a_dto_vista,
    mapear_dto_vista_a_clase_dominio,
)


def test_modelos_qt_no_importan_dominio() -> None:
    base = Path("presentacion/modelos_qt")
    for archivo in base.glob("*.py"):
        contenido = archivo.read_text(encoding="utf-8")
        assert "from dominio" not in contenido
        assert "import dominio" not in contenido


def test_mapper_convierte_dominio_a_dto() -> None:
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

    assert isinstance(dto, DtoVistaClase)
    assert dto.nombre == "Cliente"
    assert dto.atributos == [
        DtoVistaAtributo(
            nombre="edad",
            tipo="int",
            obligatorio=False,
            valor_por_defecto="18",
        )
    ]


def test_mapper_convierte_dto_a_dominio() -> None:
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

    assert isinstance(clase_dominio, EspecificacionClase)
    assert clase_dominio.nombre == "Pedido"
    assert len(clase_dominio.atributos) == 1
    assert clase_dominio.atributos[0].nombre == "total"
    assert clase_dominio.atributos[0].tipo == "float"
    assert clase_dominio.atributos[0].obligatorio is True
    assert clase_dominio.atributos[0].valor_por_defecto is None

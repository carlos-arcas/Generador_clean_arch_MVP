"""Adaptador anti-corrupción para mapear dominio hacia DTOs de vista."""

from __future__ import annotations

from dominio.especificacion import EspecificacionAtributo, EspecificacionClase
from presentacion.dtos import DtoVistaAtributo, DtoVistaClase


def mapear_clase_dominio_a_dto_vista(clase_dominio: EspecificacionClase) -> DtoVistaClase:
    """Convierte una entidad de dominio de clase a DTO de vista."""

    return DtoVistaClase(
        nombre=clase_dominio.nombre,
        atributos=[
            DtoVistaAtributo(
                nombre=atributo.nombre,
                tipo=atributo.tipo,
                obligatorio=atributo.obligatorio,
                valor_por_defecto=atributo.valor_por_defecto or "",
            )
            for atributo in clase_dominio.atributos
        ],
    )


def mapear_dto_vista_a_clase_dominio(dto: DtoVistaClase) -> EspecificacionClase:
    """Convierte un DTO de vista de clase a entidad de dominio."""

    return EspecificacionClase(
        nombre=dto.nombre,
        atributos=[
            EspecificacionAtributo(
                nombre=atributo.nombre,
                tipo=atributo.tipo,
                obligatorio=atributo.obligatorio,
                valor_por_defecto=atributo.valor_por_defecto or None,
            )
            for atributo in dto.atributos
        ],
    )

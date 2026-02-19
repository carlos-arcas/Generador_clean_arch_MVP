"""Mapeos entre entidades de dominio y DTOs de presentación."""

from __future__ import annotations

from dominio.especificacion import EspecificacionAtributo, EspecificacionClase
from presentacion.dtos import DtoAtributoPresentacion, DtoClasePresentacion


def mapear_clase_dominio_a_dto(clase_dominio: EspecificacionClase) -> DtoClasePresentacion:
    """Convierte una entidad de dominio de clase en DTO de presentación."""

    return DtoClasePresentacion(
        nombre=clase_dominio.nombre,
        atributos=[
            DtoAtributoPresentacion(
                nombre=atributo.nombre,
                tipo=atributo.tipo,
                obligatorio=atributo.obligatorio,
                valor_por_defecto=atributo.valor_por_defecto or "",
            )
            for atributo in clase_dominio.atributos
        ],
    )


def mapear_dto_a_clase_dominio(dto: DtoClasePresentacion) -> EspecificacionClase:
    """Convierte un DTO de presentación de clase en entidad de dominio."""

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

"""Mapeadores de aplicación para aislamiento entre capas."""

from aplicacion.mapeadores.mapeador_dominio_a_presentacion import (
    mapear_clase_dominio_a_dto,
    mapear_dto_a_clase_dominio,
)

__all__ = ["mapear_clase_dominio_a_dto", "mapear_dto_a_clase_dominio"]

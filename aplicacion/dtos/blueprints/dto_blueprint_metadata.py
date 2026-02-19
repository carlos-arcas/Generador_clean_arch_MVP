"""DTOs para metadata declarativa de blueprints."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


TipoBlueprint = Literal[
    "CRUD_FULL",
    "CRUD_BASE",
    "PERSISTENCIA",
    "API",
    "EXPORT",
    "PLUGIN",
]


@dataclass(frozen=True)
class DtoBlueprintMetadata:
    nombre: str
    descripcion: str
    tipo: TipoBlueprint
    entidad: str | None
    requiere_clases: bool
    genera_capas: list[str] = field(default_factory=list)
    incompatible_con_tipos: list[str] = field(default_factory=list)
    incompatible_con_mismo_tipo_y_entidad: bool = False
    compatible_con: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DtoConflictoBlueprint:
    codigo: str
    blueprint_a: str
    blueprint_b: str | None
    motivo: str
    accion_sugerida: str
    regla_violada: str
    tipo_blueprint_a: str | None = None
    tipo_blueprint_b: str | None = None
    entidad_a: str | None = None
    entidad_b: str | None = None


@dataclass(frozen=True)
class DtoResultadoValidacionCompatibilidad:
    es_valido: bool
    conflictos: list[DtoConflictoBlueprint] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

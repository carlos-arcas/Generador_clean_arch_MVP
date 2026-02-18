"""DTO de entrada para construir especificaciones de proyecto."""

from __future__ import annotations

from dataclasses import dataclass, field

from aplicacion.dtos.proyecto.dto_clase import DtoClase


@dataclass(frozen=True)
class DtoProyectoEntrada:
    """Datos simples recopilados desde UI para generar un proyecto."""

    nombre_proyecto: str
    ruta_destino: str
    descripcion: str = ""
    version: str = "0.1.0"
    clases: list[DtoClase] = field(default_factory=list)

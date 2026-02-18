"""Modelos de dominio para especificación y planificación de generación."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import List

PATRON_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


class ErrorValidacionDominio(ValueError):
    """Error de validación para entidades de dominio."""


@dataclass
class EspecificacionProyecto:
    """Define los datos mínimos requeridos para generar un proyecto base."""

    nombre_proyecto: str
    ruta_destino: str
    descripcion: str | None = None
    version: str = "0.1.0"

    def validar(self) -> None:
        """Valida la especificación del proyecto y falla si hay datos inválidos."""
        if not self.nombre_proyecto or not self.nombre_proyecto.strip():
            raise ErrorValidacionDominio("El nombre del proyecto no puede estar vacío.")

        if not self.ruta_destino or not self.ruta_destino.strip():
            raise ErrorValidacionDominio("La ruta de destino no puede estar vacía.")

        if not PATRON_SEMVER.match(self.version):
            raise ErrorValidacionDominio("La versión debe cumplir el formato X.Y.Z.")


@dataclass(frozen=True)
class ArchivoGenerado:
    """Representa un archivo a crear dentro del plan de generación."""

    ruta_relativa: str
    contenido_texto: str


@dataclass
class PlanGeneracion:
    """Lista de archivos que serán generados para construir un proyecto base."""

    archivos: List[ArchivoGenerado] = field(default_factory=list)

    def obtener_rutas(self) -> list[str]:
        """Retorna todas las rutas relativas incluidas en el plan."""
        return [archivo.ruta_relativa for archivo in self.archivos]

    def comprobar_duplicados(self) -> None:
        """Valida que no existan rutas duplicadas en el plan."""
        rutas = self.obtener_rutas()
        rutas_duplicadas = {ruta for ruta in rutas if rutas.count(ruta) > 1}
        if rutas_duplicadas:
            raise ErrorValidacionDominio(
                f"El plan contiene rutas duplicadas: {sorted(rutas_duplicadas)}"
            )

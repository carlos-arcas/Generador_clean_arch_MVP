"""Modelos de dominio para especificación y planificación de generación."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, List

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

    def agregar_archivo(self, archivo: ArchivoGenerado) -> None:
        """Agrega un archivo al plan actual."""
        self.archivos.append(archivo)

    def fusionar(self, otro_plan: PlanGeneracion) -> PlanGeneracion:
        """Fusiona este plan con otro y retorna un nuevo plan compuesto."""
        plan_fusionado = PlanGeneracion(archivos=[*self.archivos, *otro_plan.archivos])
        plan_fusionado.validar_sin_conflictos()
        return plan_fusionado

    def obtener_rutas(self) -> list[str]:
        """Retorna todas las rutas relativas incluidas en el plan."""
        return [archivo.ruta_relativa for archivo in self.archivos]

    def validar_sin_conflictos(self) -> None:
        """Valida que no existan rutas duplicadas en el plan."""
        rutas = self.obtener_rutas()
        rutas_duplicadas = {ruta for ruta in rutas if rutas.count(ruta) > 1}
        if rutas_duplicadas:
            raise ErrorValidacionDominio(
                f"El plan contiene rutas duplicadas: {sorted(rutas_duplicadas)}"
            )

    def comprobar_duplicados(self) -> None:
        """Compatibilidad retroactiva: delega a validar_sin_conflictos."""
        self.validar_sin_conflictos()


@dataclass(frozen=True)
class EntradaManifest:
    """Representa una entrada de archivo en el manifest generado."""

    ruta_relativa: str
    hash_sha256: str

    def __post_init__(self) -> None:
        if not self.ruta_relativa.strip():
            raise ErrorValidacionDominio("La ruta del manifest no puede estar vacía.")
        if not self.hash_sha256.strip():
            raise ErrorValidacionDominio("El hash SHA256 es obligatorio en el manifest.")


@dataclass
class ManifestProyecto:
    """Representa la metadata de generación del proyecto."""

    version_generador: str
    blueprints_usados: list[str]
    archivos: list[EntradaManifest]
    timestamp_generacion: str
    opciones: dict[str, Any]

    def __post_init__(self) -> None:
        rutas = [entrada.ruta_relativa for entrada in self.archivos]
        duplicadas = {ruta for ruta in rutas if rutas.count(ruta) > 1}
        if duplicadas:
            raise ErrorValidacionDominio(
                f"El manifest contiene rutas duplicadas: {sorted(duplicadas)}"
            )

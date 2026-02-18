"""Modelos de dominio para describir el manifest de artefactos generados."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dominio.especificacion import ErrorValidacionDominio


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

    def obtener_clases_generadas(self) -> list[str]:
        """Retorna clases detectadas desde archivos de entidades en el manifest."""
        prefijo = "dominio/entidades/"
        clases_generadas: list[str] = []
        for entrada in self.archivos:
            ruta = entrada.ruta_relativa
            if not ruta.startswith(prefijo) or not ruta.endswith(".py"):
                continue
            nombre_snake = ruta[len(prefijo) : -3]
            if not nombre_snake:
                continue
            clase = "".join(fragmento.capitalize() for fragmento in nombre_snake.split("_"))
            clases_generadas.append(clase)
        return clases_generadas

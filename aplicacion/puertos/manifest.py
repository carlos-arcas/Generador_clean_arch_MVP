"""Puertos para lectura/escritura de manifest de proyectos generados."""

from __future__ import annotations

from abc import ABC, abstractmethod

from dominio.modelos import ManifestProyecto


class LectorManifest(ABC):
    """Contrato para cargar manifest.json desde una ubicación de proyecto."""

    @abstractmethod
    def leer(self, ruta_proyecto: str) -> ManifestProyecto:
        """Lee y retorna el manifest del proyecto."""


class EscritorManifest(ABC):
    """Contrato para persistir manifest.json de forma segura."""

    @abstractmethod
    def escribir(self, ruta_proyecto: str, manifest: ManifestProyecto) -> None:
        """Persiste el manifest del proyecto."""

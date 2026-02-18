"""Puerto para operaciones de sistema de archivos."""

from __future__ import annotations

from abc import ABC, abstractmethod


class SistemaArchivos(ABC):
    """Define el contrato para escritura y creación de directorios."""

    @abstractmethod
    def escribir_texto_atomico(self, ruta_absoluta: str, contenido: str) -> None:
        """Escribe texto de forma atómica en una ruta absoluta."""

    @abstractmethod
    def asegurar_directorio(self, ruta_absoluta: str) -> None:
        """Asegura la existencia de un directorio."""

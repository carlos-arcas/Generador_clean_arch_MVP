"""Abstracciones para almacenamiento de credenciales."""

from __future__ import annotations

from typing import Protocol

from dominio.seguridad.credencial import Credencial


class RepositorioCredenciales(Protocol):
    """Puerto de almacenamiento seguro de credenciales."""

    def guardar(self, credencial: Credencial) -> None:
        ...

    def obtener(self, identificador: str) -> Credencial | None:
        ...

    def eliminar(self, identificador: str) -> None:
        ...

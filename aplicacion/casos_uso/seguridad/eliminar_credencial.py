"""Caso de uso para eliminación de credenciales."""

from __future__ import annotations

from .repositorio_credenciales import RepositorioCredenciales


class EliminarCredencial:
    """Elimina una credencial por identificador."""

    def __init__(self, repositorio: RepositorioCredenciales) -> None:
        self._repositorio = repositorio

    def ejecutar(self, identificador: str) -> None:
        self._repositorio.eliminar(identificador)

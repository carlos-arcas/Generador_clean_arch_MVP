"""Caso de uso para recuperar credenciales."""

from __future__ import annotations

from dominio.seguridad.credencial import Credencial

from .repositorio_credenciales import RepositorioCredenciales


class ObtenerCredencial:
    """Recupera una credencial por identificador."""

    def __init__(self, repositorio: RepositorioCredenciales) -> None:
        self._repositorio = repositorio

    def ejecutar(self, identificador: str) -> Credencial | None:
        return self._repositorio.obtener(identificador)

"""Repositorio de credenciales en memoria (fallback/testing)."""

from __future__ import annotations

from dominio.seguridad.credencial import Credencial


class RepositorioCredencialesMemoria:
    """Mantiene credenciales solo durante la vida del proceso."""

    def __init__(self) -> None:
        self._credenciales: dict[str, Credencial] = {}

    def guardar(self, credencial: Credencial) -> None:
        self._credenciales[credencial.identificador] = credencial

    def obtener(self, identificador: str) -> Credencial | None:
        return self._credenciales.get(identificador)

    def eliminar(self, identificador: str) -> None:
        self._credenciales.pop(identificador, None)

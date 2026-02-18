"""Caso de uso para guardar credenciales."""

from __future__ import annotations

from dominio.seguridad.credencial import Credencial

from .repositorio_credenciales import RepositorioCredenciales


class GuardarCredencial:
    """Persiste una credencial en el repositorio configurado."""

    def __init__(self, repositorio: RepositorioCredenciales) -> None:
        self._repositorio = repositorio

    def ejecutar(self, credencial: Credencial) -> None:
        self._repositorio.guardar(credencial)

    def ejecutar_desde_datos(self, *, identificador: str, usuario: str, secreto: str, tipo: str) -> None:
        self.ejecutar(
            Credencial(
                identificador=identificador,
                usuario=usuario,
                secreto=secreto,
                tipo=tipo,
            )
        )

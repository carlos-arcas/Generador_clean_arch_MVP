"""Entidades de credenciales sensibles."""

from __future__ import annotations

from typing import Any


class Credencial:
    """Representa una credencial evitando exposición accidental del secreto."""

    __slots__ = ("identificador", "usuario", "_secreto", "tipo")

    def __init__(self, identificador: str, usuario: str, secreto: str, tipo: str) -> None:
        self.identificador = identificador.strip()
        self.usuario = usuario.strip()
        self._secreto = secreto
        self.tipo = tipo.strip()

    @property
    def secreto(self) -> str:
        return self._secreto

    def a_dict_publico(self) -> dict[str, str]:
        """Devuelve una vista serializable sin el secreto."""
        return {
            "identificador": self.identificador,
            "usuario": self.usuario,
            "tipo": self.tipo,
        }

    def __repr__(self) -> str:
        return (
            "Credencial("
            f"identificador={self.identificador!r}, "
            f"usuario={self.usuario!r}, "
            "secreto='***', "
            f"tipo={self.tipo!r}"
            ")"
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Credencial):
            return False
        return (
            self.identificador == other.identificador
            and self.usuario == other.usuario
            and self._secreto == other._secreto
            and self.tipo == other.tipo
        )

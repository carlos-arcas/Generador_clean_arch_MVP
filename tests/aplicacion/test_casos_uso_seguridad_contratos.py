from __future__ import annotations

from aplicacion.casos_uso.seguridad.eliminar_credencial import EliminarCredencial
from aplicacion.casos_uso.seguridad.obtener_credencial import ObtenerCredencial
from dominio.seguridad.credencial import Credencial


class _RepositorioCredencialesFake:
    def __init__(self) -> None:
        self._data: dict[str, Credencial] = {}

    def guardar(self, credencial: Credencial) -> None:
        self._data[credencial.identificador] = credencial

    def obtener(self, identificador: str) -> Credencial | None:
        return self._data.get(identificador)

    def eliminar(self, identificador: str) -> None:
        self._data.pop(identificador, None)


def test_obtener_y_eliminar_credencial_respetan_contrato() -> None:
    repo = _RepositorioCredencialesFake()
    credencial = Credencial("github", "bot", "secret", "token")
    repo.guardar(credencial)

    obtener = ObtenerCredencial(repo)
    eliminar = EliminarCredencial(repo)

    assert obtener.ejecutar("github") == credencial
    eliminar.ejecutar("github")
    assert obtener.ejecutar("github") is None

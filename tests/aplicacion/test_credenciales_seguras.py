from aplicacion.casos_uso.seguridad import GuardarCredencial, ObtenerCredencial
from dominio.seguridad import Credencial
from infraestructura.seguridad import RepositorioCredencialesMemoria


def test_guardar_credencial_modo_memoria() -> None:
    repositorio = RepositorioCredencialesMemoria()
    caso_uso = GuardarCredencial(repositorio)

    credencial = Credencial("id_demo", "usuario_demo", "super-secreto", "SQLite")
    caso_uso.ejecutar(credencial)

    assert repositorio.obtener("id_demo") == credencial


def test_recuperar_credencial() -> None:
    repositorio = RepositorioCredencialesMemoria()
    repositorio.guardar(Credencial("id_demo", "usuario_demo", "super-secreto", "CRM"))

    caso_uso = ObtenerCredencial(repositorio)
    recuperada = caso_uso.ejecutar("id_demo")

    assert recuperada is not None
    assert recuperada.usuario == "usuario_demo"
    assert recuperada.secreto == "super-secreto"


def test_repr_credencial_no_expone_secreto() -> None:
    credencial = Credencial("id_demo", "usuario_demo", "ultra-secreto", "DB")

    representacion = repr(credencial)

    assert "ultra-secreto" not in representacion
    assert "***" in representacion

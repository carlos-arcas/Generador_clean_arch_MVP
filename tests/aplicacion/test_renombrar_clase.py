import pytest

from aplicacion.casos_uso.gestion_clases import AgregarClase, RenombrarClase
from dominio.modelos import ErrorValidacionDominio, EspecificacionClase
from infraestructura.repositorio_especificacion_proyecto_en_memoria import (
    RepositorioEspecificacionProyectoEnMemoria,
)


def test_renombrar_clase_ok() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()
    clase = AgregarClase(repo).ejecutar(EspecificacionClase(nombre="Cliente"))

    renombrada = RenombrarClase(repo).ejecutar(clase.id_interno, "ClienteVip")

    assert renombrada.nombre == "ClienteVip"


def test_renombrar_clase_nombre_invalido_falla() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()
    clase = AgregarClase(repo).ejecutar(EspecificacionClase(nombre="Cliente"))

    with pytest.raises(ErrorValidacionDominio, match="PascalCase"):
        RenombrarClase(repo).ejecutar(clase.id_interno, "cliente")

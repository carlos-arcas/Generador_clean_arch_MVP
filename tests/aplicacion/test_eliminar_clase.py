import pytest

from aplicacion.casos_uso.gestion_clases import AgregarClase, EliminarClase
from dominio.modelos import ErrorValidacionDominio, EspecificacionClase
from infraestructura.repositorio_especificacion_proyecto_en_memoria import (
    RepositorioEspecificacionProyectoEnMemoria,
)


def test_eliminar_clase_ok() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()
    clase = AgregarClase(repo).ejecutar(EspecificacionClase(nombre="Cliente"))

    EliminarClase(repo).ejecutar(clase.id_interno)

    with pytest.raises(ErrorValidacionDominio, match="No existe"):
        repo.obtener().obtener_clase(clase.id_interno)


def test_eliminar_clase_inexistente_falla() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()

    with pytest.raises(ErrorValidacionDominio, match="No existe"):
        EliminarClase(repo).ejecutar("id-que-no-existe")

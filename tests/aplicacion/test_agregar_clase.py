import pytest

from aplicacion.casos_uso.gestion_clases import AgregarClase, ListarClases, ObtenerClaseDetallada
from dominio.modelos import ErrorValidacionDominio, EspecificacionClase
from infraestructura.repositorio_especificacion_proyecto_en_memoria import (
    RepositorioEspecificacionProyectoEnMemoria,
)


def test_agregar_clase_ok() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()

    clase = AgregarClase(repo).ejecutar(EspecificacionClase(nombre="Cliente"))

    assert repo.obtener().obtener_clase(clase.id_interno).nombre == "Cliente"


def test_agregar_clase_duplicada_falla() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()
    caso = AgregarClase(repo)
    caso.ejecutar(EspecificacionClase(nombre="Cliente"))

    with pytest.raises(ErrorValidacionDominio, match="clase"):
        caso.ejecutar(EspecificacionClase(nombre="Cliente"))


def test_listar_y_obtener_clase_detallada() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()
    clase = AgregarClase(repo).ejecutar(EspecificacionClase(nombre="Pedido"))

    clases = ListarClases(repo).ejecutar()
    detalle = ObtenerClaseDetallada(repo).ejecutar(clase.id_interno)

    assert len(clases) == 1
    assert detalle.nombre == "Pedido"

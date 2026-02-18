import pytest

from aplicacion.casos_uso.gestion_clases import AgregarAtributo, AgregarClase, EliminarAtributo
from dominio.modelos import ErrorValidacionDominio, EspecificacionAtributo, EspecificacionClase
from infraestructura.repositorio_especificacion_proyecto_en_memoria import (
    RepositorioEspecificacionProyectoEnMemoria,
)


def test_eliminar_atributo_ok() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()
    clase = AgregarClase(repo).ejecutar(EspecificacionClase(nombre="Factura"))
    atributo = AgregarAtributo(repo).ejecutar(
        clase.id_interno,
        EspecificacionAtributo(nombre="total", tipo="float", obligatorio=True),
    )

    EliminarAtributo(repo).ejecutar(clase.id_interno, atributo.id_interno)

    with pytest.raises(ErrorValidacionDominio, match="No existe"):
        repo.obtener().obtener_clase(clase.id_interno).obtener_atributo(atributo.id_interno)


def test_eliminar_atributo_inexistente_falla() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()
    clase = AgregarClase(repo).ejecutar(EspecificacionClase(nombre="Factura"))

    with pytest.raises(ErrorValidacionDominio, match="atributo"):
        EliminarAtributo(repo).ejecutar(clase.id_interno, "inexistente")

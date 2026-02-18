import pytest

from aplicacion.casos_uso.gestion_clases import AgregarAtributo, AgregarClase
from dominio.modelos import ErrorValidacionDominio, EspecificacionAtributo, EspecificacionClase
from infraestructura.repositorio_especificacion_proyecto_en_memoria import (
    RepositorioEspecificacionProyectoEnMemoria,
)


def test_agregar_atributo_ok() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()
    clase = AgregarClase(repo).ejecutar(EspecificacionClase(nombre="Cliente"))

    atributo = AgregarAtributo(repo).ejecutar(
        clase.id_interno,
        EspecificacionAtributo(nombre="email", tipo="str", obligatorio=True),
    )

    assert repo.obtener().obtener_clase(clase.id_interno).obtener_atributo(atributo.id_interno)


def test_agregar_atributo_duplicado_falla() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()
    clase = AgregarClase(repo).ejecutar(EspecificacionClase(nombre="Cliente"))
    caso = AgregarAtributo(repo)
    caso.ejecutar(
        clase.id_interno,
        EspecificacionAtributo(nombre="email", tipo="str", obligatorio=True),
    )

    with pytest.raises(ErrorValidacionDominio, match="atributo"):
        caso.ejecutar(
            clase.id_interno,
            EspecificacionAtributo(nombre="email", tipo="str", obligatorio=False),
        )

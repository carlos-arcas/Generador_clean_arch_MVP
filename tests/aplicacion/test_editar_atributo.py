import pytest

from aplicacion.casos_uso.gestion_clases import AgregarAtributo, AgregarClase, EditarAtributo
from dominio.modelos import ErrorValidacionDominio, EspecificacionAtributo, EspecificacionClase
from infraestructura.repositorio_especificacion_proyecto_en_memoria import (
    RepositorioEspecificacionProyectoEnMemoria,
)


def test_editar_atributo_ok() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()
    clase = AgregarClase(repo).ejecutar(EspecificacionClase(nombre="Factura"))
    atributo = AgregarAtributo(repo).ejecutar(
        clase.id_interno,
        EspecificacionAtributo(nombre="total", tipo="float", obligatorio=True),
    )

    editado = EditarAtributo(repo).ejecutar(
        id_clase=clase.id_interno,
        id_atributo=atributo.id_interno,
        nombre="montoTotal",
        tipo="decimal",
        obligatorio=False,
        valor_por_defecto="0",
    )

    assert editado.nombre == "montoTotal"


def test_editar_atributo_inexistente_falla() -> None:
    repo = RepositorioEspecificacionProyectoEnMemoria()
    clase = AgregarClase(repo).ejecutar(EspecificacionClase(nombre="Factura"))

    with pytest.raises(ErrorValidacionDominio, match="atributo"):
        EditarAtributo(repo).ejecutar(
            id_clase=clase.id_interno,
            id_atributo="inexistente",
            nombre="montoTotal",
            tipo="decimal",
            obligatorio=False,
            valor_por_defecto=None,
        )

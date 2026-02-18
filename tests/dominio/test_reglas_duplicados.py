import pytest

from dominio.modelos import (
    ErrorValidacionDominio,
    EspecificacionAtributo,
    EspecificacionClase,
    EspecificacionProyecto,
)


def test_no_permite_atributos_duplicados_por_nombre() -> None:
    clase = EspecificacionClase(nombre="Cliente")
    clase.agregar_atributo(EspecificacionAtributo(nombre="id", tipo="str", obligatorio=True))

    with pytest.raises(ErrorValidacionDominio, match="atributo"):
        clase.agregar_atributo(
            EspecificacionAtributo(nombre="id", tipo="int", obligatorio=False)
        )


def test_no_permite_clases_duplicadas_por_nombre() -> None:
    proyecto = EspecificacionProyecto(nombre_proyecto="demo", ruta_destino="/tmp/demo")
    proyecto.agregar_clase(EspecificacionClase(nombre="Cliente"))

    with pytest.raises(ErrorValidacionDominio, match="clase"):
        proyecto.agregar_clase(EspecificacionClase(nombre="Cliente"))


def test_renombrar_clase_a_nombre_existente_falla() -> None:
    proyecto = EspecificacionProyecto(nombre_proyecto="demo", ruta_destino="/tmp/demo")
    cliente = EspecificacionClase(nombre="Cliente")
    pedido = EspecificacionClase(nombre="Pedido")
    proyecto.agregar_clase(cliente)
    proyecto.agregar_clase(pedido)

    with pytest.raises(ErrorValidacionDominio, match="clase"):
        proyecto.renombrar_clase(pedido.id_interno, "Cliente")

import pytest

from dominio.modelos import ErrorValidacionDominio, EspecificacionAtributo, EspecificacionClase


def test_clase_valida_permite_lista_vacia() -> None:
    clase = EspecificacionClase(nombre="Cliente")

    assert clase.atributos == []


def test_clase_falla_si_nombre_no_es_pascal_case() -> None:
    with pytest.raises(ErrorValidacionDominio, match="PascalCase"):
        EspecificacionClase(nombre="cliente")


def test_clase_agrega_y_obtiene_atributo() -> None:
    clase = EspecificacionClase(nombre="Pedido")
    atributo = EspecificacionAtributo(nombre="id", tipo="str", obligatorio=True)

    clase.agregar_atributo(atributo)

    assert clase.obtener_atributo(atributo.id_interno).nombre == "id"


def test_clase_editar_atributo() -> None:
    clase = EspecificacionClase(nombre="Factura")
    atributo = EspecificacionAtributo(nombre="total", tipo="float", obligatorio=True)
    clase.agregar_atributo(atributo)

    editado = clase.editar_atributo(
        id_interno=atributo.id_interno,
        nombre="monto",
        tipo="decimal",
        obligatorio=False,
        valor_por_defecto="0",
    )

    assert editado.nombre == "monto"
    assert clase.obtener_atributo(atributo.id_interno).tipo == "decimal"


def test_clase_elimina_atributo() -> None:
    clase = EspecificacionClase(nombre="Producto")
    atributo = EspecificacionAtributo(nombre="sku", tipo="str", obligatorio=True)
    clase.agregar_atributo(atributo)

    clase.eliminar_atributo(atributo.id_interno)

    with pytest.raises(ErrorValidacionDominio, match="No existe"):
        clase.obtener_atributo(atributo.id_interno)

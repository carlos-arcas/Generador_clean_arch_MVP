import pytest

from dominio.modelos import ErrorValidacionDominio, EspecificacionAtributo


def test_atributo_valido() -> None:
    atributo = EspecificacionAtributo(nombre="edad", tipo="int", obligatorio=True)

    assert atributo.nombre == "edad"
    assert atributo.valor_por_defecto is None


def test_atributo_falla_si_nombre_vacio() -> None:
    with pytest.raises(ErrorValidacionDominio, match="nombre"):
        EspecificacionAtributo(nombre="", tipo="str", obligatorio=False)


def test_atributo_falla_si_nombre_contiene_espacios() -> None:
    with pytest.raises(ErrorValidacionDominio, match="espacios"):
        EspecificacionAtributo(nombre="nombre completo", tipo="str", obligatorio=False)


def test_atributo_falla_si_tipo_vacio() -> None:
    with pytest.raises(ErrorValidacionDominio, match="tipo"):
        EspecificacionAtributo(nombre="nombre", tipo="", obligatorio=False)

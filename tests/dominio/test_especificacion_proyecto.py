import pytest

from dominio.modelos import ErrorValidacionDominio, EspecificacionProyecto


def test_especificacion_valida_no_lanza_error() -> None:
    especificacion = EspecificacionProyecto(
        nombre_proyecto="mi_proyecto",
        ruta_destino="/tmp/salida",
        descripcion="demo",
        version="1.2.3",
    )

    especificacion.validar()


def test_especificacion_falla_si_nombre_vacio() -> None:
    especificacion = EspecificacionProyecto(
        nombre_proyecto="  ", ruta_destino="/tmp/salida", version="1.2.3"
    )

    with pytest.raises(ErrorValidacionDominio, match="nombre"):
        especificacion.validar()


def test_especificacion_falla_si_ruta_vacia() -> None:
    especificacion = EspecificacionProyecto(
        nombre_proyecto="ok", ruta_destino="", version="1.2.3"
    )

    with pytest.raises(ErrorValidacionDominio, match="ruta"):
        especificacion.validar()


def test_especificacion_falla_si_version_no_semver() -> None:
    especificacion = EspecificacionProyecto(
        nombre_proyecto="ok", ruta_destino="/tmp/salida", version="1.0"
    )

    with pytest.raises(ErrorValidacionDominio, match="X.Y.Z"):
        especificacion.validar()

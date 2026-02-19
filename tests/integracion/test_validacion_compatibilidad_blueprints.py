from __future__ import annotations

from aplicacion.casos_uso.validar_compatibilidad_blueprints import ValidarCompatibilidadBlueprints
from infraestructura.blueprints.metadata_registry import obtener_metadata_blueprints


def _caso() -> ValidarCompatibilidadBlueprints:
    return ValidarCompatibilidadBlueprints(obtener_metadata_blueprints())


def test_crud_json_y_crud_sqlite_falla_con_conflicto_declarativo() -> None:
    salida = _caso().ejecutar(["crud_json", "crud_sqlite"], hay_clases=True)

    assert salida.es_valido is False
    assert any(conflicto.codigo == "CON-DECL-001" for conflicto in salida.conflictos)


def test_crud_json_solo_es_compatible() -> None:
    salida = _caso().ejecutar(["crud_json"], hay_clases=True)

    assert salida.es_valido is True
    assert salida.conflictos == []


def test_api_fastapi_con_crud_json_es_compatible() -> None:
    salida = _caso().ejecutar(["api_fastapi", "crud_json"], hay_clases=True)

    assert salida.es_valido is True


def test_blueprint_que_requiere_clases_sin_clases_falla() -> None:
    salida = _caso().ejecutar(["crud_json"], hay_clases=False)

    assert salida.es_valido is False
    assert any(conflicto.codigo == "VAL-DECL-001" for conflicto in salida.conflictos)

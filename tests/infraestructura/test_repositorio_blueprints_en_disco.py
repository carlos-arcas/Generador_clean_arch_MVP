from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco


def test_listar_blueprints_carga_blueprint_base() -> None:
    repositorio = RepositorioBlueprintsEnDisco("blueprints")

    blueprints = repositorio.listar_blueprints()

    nombres = [blueprint.nombre() for blueprint in blueprints]
    assert "base_clean_arch" in nombres
    assert "crud_json" in nombres
    assert "crud_sqlite" in nombres


def test_obtener_por_nombre_retorna_blueprint() -> None:
    repositorio = RepositorioBlueprintsEnDisco("blueprints")

    blueprint = repositorio.obtener_por_nombre("base_clean_arch")

    assert blueprint.version() == "1.0.0"

from __future__ import annotations

from infraestructura.bootstrap.bootstrap_cli import ContenedorCli, construir_contenedor_cli


def test_construir_contenedor_cli_devuelve_objeto_valido() -> None:
    contenedor = construir_contenedor_cli()

    assert isinstance(contenedor, ContenedorCli)


def test_contenedor_cli_expone_casos_de_uso_principales() -> None:
    contenedor = construir_contenedor_cli()

    assert contenedor.generar_proyecto_mvp is not None
    assert contenedor.auditar_proyecto is not None
    assert contenedor.crear_plan_desde_blueprints is not None


def test_cli_no_instancia_dependencias_no_necesarias_de_credenciales(monkeypatch) -> None:
    llamado = {"crear": 0}

    def _crear_repositorio(self):
        llamado["crear"] += 1
        raise AssertionError("No debería crear repositorio de credenciales en CLI")

    monkeypatch.setattr(
        "infraestructura.bootstrap.bootstrap_base.SelectorRepositorioCredenciales.crear",
        _crear_repositorio,
    )

    construir_contenedor_cli()

    assert llamado["crear"] == 0

from __future__ import annotations

import json

import pytest

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.puertos.blueprint import Blueprint, RepositorioBlueprints
from aplicacion.errores import ErrorValidacion
from dominio.modelos import EspecificacionProyecto
from infraestructura.plugins.descubridor_plugins import DescubridorPlugins


class RepositorioVacio(RepositorioBlueprints):
    def listar_blueprints(self) -> list[Blueprint]:
        return []

    def obtener_por_nombre(self, nombre: str) -> Blueprint:
        raise ValueError(nombre)


def test_plugin_valido_se_detecta(tmp_path) -> None:
    ruta_plugin = tmp_path / "plugins" / "api_fastapi"
    (ruta_plugin / "templates").mkdir(parents=True)
    (ruta_plugin / "templates" / "archivo.txt").write_text("ok", encoding="utf-8")
    (ruta_plugin / "blueprint.json").write_text(
        json.dumps(
            {
                "nombre": "api_fastapi",
                "version": "1.0.0",
                "descripcion": "API",
                "compatible_con": ["base_clean_arch"],
                "capas": ["presentacion"],
                "requiere": [],
            }
        ),
        encoding="utf-8",
    )

    descubridor = DescubridorPlugins(str(tmp_path / "plugins"))

    plugins = descubridor.listar_plugins()

    assert [plugin.nombre for plugin in plugins] == ["api_fastapi"]


def test_plugin_sin_blueprint_json_se_ignora(tmp_path, caplog: pytest.LogCaptureFixture) -> None:
    (tmp_path / "plugins" / "sin_manifest").mkdir(parents=True)

    descubridor = DescubridorPlugins(str(tmp_path / "plugins"))

    plugins = descubridor.listar_plugins()

    assert plugins == []
    assert "Plugin ignorado sin blueprint.json" in caplog.text


def test_plugin_incompatible_retorna_error_controlado(tmp_path) -> None:
    ruta_plugin = tmp_path / "plugins" / "api_fastapi"
    (ruta_plugin / "templates").mkdir(parents=True)
    (ruta_plugin / "templates" / "archivo.txt").write_text("ok", encoding="utf-8")
    (ruta_plugin / "blueprint.json").write_text(
        json.dumps(
            {
                "nombre": "api_fastapi",
                "version": "1.0.0",
                "descripcion": "API",
                "compatible_con": ["base_clean_arch"],
                "capas": ["presentacion"],
                "requiere": [],
            }
        ),
        encoding="utf-8",
    )

    caso_uso = CrearPlanDesdeBlueprints(
        RepositorioVacio(),
        descubridor_plugins=DescubridorPlugins(str(tmp_path / "plugins")),
    )

    with pytest.raises(ErrorValidacion, match="Plugin incompatible"):
        caso_uso.ejecutar(EspecificacionProyecto("Demo", "/tmp/demo"), ["api_fastapi"])

from __future__ import annotations

import json

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from dominio.modelos import EspecificacionProyecto
from infraestructura.plugins.descubridor_plugins import DescubridorPlugins
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco


def test_generar_plan_incluye_archivos_de_plugin_externo(tmp_path) -> None:
    ruta_plugin = tmp_path / "plugins" / "api_fastapi"
    (ruta_plugin / "templates" / "presentacion").mkdir(parents=True)
    (ruta_plugin / "templates" / "presentacion" / "main.py").write_text(
        "print('plugin')\n", encoding="utf-8"
    )
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
        RepositorioBlueprintsEnDisco("blueprints"),
        descubridor_plugins=DescubridorPlugins(str(tmp_path / "plugins")),
    )

    plan = caso_uso.ejecutar(
        EspecificacionProyecto(nombre_proyecto="Demo", ruta_destino="/tmp/demo"),
        ["base_clean_arch", "api_fastapi"],
    )

    assert "presentacion/main.py" in plan.obtener_rutas()

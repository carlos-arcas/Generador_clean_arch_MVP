from __future__ import annotations

import json
from pathlib import Path

from infraestructura.bootstrap.bootstrap_cli import construir_contenedor_cli


def test_auditor_finalizacion_mide_duraciones(tmp_path: Path) -> None:
    preset = tmp_path / "preset_ok.json"
    preset.write_text(
        json.dumps(
            {
                "especificacion": {
                    "nombre_proyecto": "demo_ok",
                    "descripcion": "",
                    "version": "1.0.0",
                    "clases": [{"nombre": "Persona", "atributos": []}],
                },
                "blueprints": ["crud_json"],
            }
        ),
        encoding="utf-8",
    )

    salida = construir_contenedor_cli().auditar_finalizacion_proyecto.ejecutar(
        ruta_preset=str(preset),
        ruta_sandbox=str(tmp_path / "sandbox"),
        ruta_evidencias=str(tmp_path / "evidencias"),
        ejecutar_smoke_test=False,
        ejecutar_auditoria_arquitectura=False,
    )

    for nombre in ["Preparación", "Carga preset", "Preflight validación entrada", "Preflight conflictos de rutas"]:
        etapa = next(item for item in salida.etapas if item.nombre == nombre)
        assert etapa.duracion_ms > 0

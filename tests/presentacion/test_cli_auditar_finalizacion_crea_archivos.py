from __future__ import annotations

import json
from pathlib import Path

from presentacion.cli.__main__ import main


def test_cli_auditar_finalizacion_crea_archivos(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    preset = tmp_path / "preset_cli.json"
    preset.write_text(
        json.dumps(
            {
                "especificacion": {
                    "nombre_proyecto": "demo_cli",
                    "descripcion": "",
                    "version": "1.0.0",
                    "clases": [{"nombre": "Persona", "atributos": []}],
                },
                "blueprints": ["crud_json", "crud_sqlite"],
            }
        ),
        encoding="utf-8",
    )

    resultado = main(
        [
            "auditar-finalizacion",
            "--preset",
            str(preset),
            "--sandbox",
            str(tmp_path / "sandbox"),
            "--evidencias",
            str(tmp_path / "docs" / "evidencias_finalizacion"),
        ]
    )

    assert resultado == 0
    carpeta = next((tmp_path / "docs" / "evidencias_finalizacion").iterdir())
    assert (carpeta / "informe.md").exists()
    assert (carpeta / "informe.json").exists()
    assert (carpeta / preset.name).exists()

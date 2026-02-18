from __future__ import annotations

import json
from pathlib import Path

from aplicacion.casos_uso.actualizar_manifest_patch import ActualizarManifestPatch
from dominio.modelos import ArchivoGenerado, PlanGeneracion
from infraestructura.calculadora_hash_real import CalculadoraHashReal
from infraestructura.manifest_en_disco import EscritorManifestSeguro, LectorManifestEnDisco


def test_actualizar_manifest_patch_agrega_solo_nuevas_entradas(tmp_path: Path) -> None:
    manifest = {
        "version_generador": "0.7.0",
        "blueprints_usados": ["crud_json@1.0.0"],
        "archivos": [
            {"ruta_relativa": "dominio/entidades/cliente.py", "hash_sha256": "hash-cliente"},
        ],
        "timestamp_generacion": "2026-01-01T00:00:00+00:00",
        "opciones": {"modo": "inicial"},
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    ruta_nueva = tmp_path / "dominio/entidades/producto.py"
    ruta_nueva.parent.mkdir(parents=True, exist_ok=True)
    ruta_nueva.write_text("class Producto: ...\n", encoding="utf-8")

    plan = PlanGeneracion([
        ArchivoGenerado("dominio/entidades/producto.py", "class Producto: ...\n"),
    ])

    actualizado = ActualizarManifestPatch(
        lector_manifest=LectorManifestEnDisco(),
        escritor_manifest=EscritorManifestSeguro(),
        calculadora_hash=CalculadoraHashReal(),
    ).ejecutar(str(tmp_path), plan)

    assert [entrada.ruta_relativa for entrada in actualizado.archivos] == [
        "dominio/entidades/cliente.py",
        "dominio/entidades/producto.py",
    ]
    assert actualizado.archivos[0].hash_sha256 == "hash-cliente"
    assert actualizado.archivos[1].hash_sha256

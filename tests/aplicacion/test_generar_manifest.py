import json
from pathlib import Path

from aplicacion.casos_uso.generar_manifest import GenerarManifest
from aplicacion.puertos.calculadora_hash import CalculadoraHash
from dominio.modelos import ArchivoGenerado, PlanGeneracion


class CalculadoraHashDoble(CalculadoraHash):
    def calcular_sha256(self, ruta_absoluta: str) -> str:
        return f"hash::{Path(ruta_absoluta).name}"


def test_generar_manifest_crea_archivo_manifest_json(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hola", encoding="utf-8")
    (tmp_path / "VERSION").write_text("0.2.0", encoding="utf-8")
    plan = PlanGeneracion(
        archivos=[
            ArchivoGenerado("README.md", "hola"),
            ArchivoGenerado("VERSION", "0.2.0"),
        ]
    )

    manifest = GenerarManifest(CalculadoraHashDoble()).ejecutar(
        plan=plan,
        ruta_destino=str(tmp_path),
        opciones={"modo": "test"},
        version_generador="0.2.0",
        blueprints_usados=["base_clean_arch@1.0.0"],
    )

    ruta_manifest = tmp_path / "manifest.json"
    assert ruta_manifest.exists()
    contenido = json.loads(ruta_manifest.read_text(encoding="utf-8"))
    assert contenido["version_generador"] == "0.2.0"
    assert len(contenido["archivos"]) == 2
    assert manifest.archivos[0].hash_sha256.startswith("hash::")

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.crear_plan_patch_desde_blueprints import CrearPlanPatchDesdeBlueprints
from aplicacion.puertos.blueprint import Blueprint, RepositorioBlueprints
from infraestructura.manifest_en_disco import LectorManifestEnDisco
from dominio.modelos import EspecificacionClase, EspecificacionProyecto, PlanGeneracion


class BlueprintNoop(Blueprint):
    def nombre(self) -> str:
        return "crud_json"

    def version(self) -> str:
        return "1.0.0"

    def validar(self, especificacion: EspecificacionProyecto) -> None:
        especificacion.validar()

    def generar_plan(self, especificacion: EspecificacionProyecto) -> PlanGeneracion:
        return PlanGeneracion()


class RepoNoop(RepositorioBlueprints):
    def listar_blueprints(self) -> list[Blueprint]:
        return [BlueprintNoop()]

    def obtener_por_nombre(self, nombre: str) -> Blueprint:
        return BlueprintNoop()


def test_patch_clase_existente_devuelve_error_controlado(tmp_path: Path) -> None:
    manifest = {
        "version_generador": "0.7.0",
        "blueprints_usados": ["crud_json@1.0.0"],
        "archivos": [
            {"ruta_relativa": "dominio/entidades/cliente.py", "hash_sha256": "hash-cliente"},
        ],
        "timestamp_generacion": "2026-01-01T00:00:00+00:00",
        "opciones": {},
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    especificacion = EspecificacionProyecto(
        nombre_proyecto="demo",
        ruta_destino=str(tmp_path),
        version="0.7.0",
        clases=[EspecificacionClase(nombre="Cliente")],
    )

    caso_uso = CrearPlanPatchDesdeBlueprints(
        lector_manifest=LectorManifestEnDisco(),
        crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepoNoop()),
    )

    with pytest.raises(ValueError, match="ya existen clases generadas"):
        caso_uso.ejecutar(especificacion, str(tmp_path))

from __future__ import annotations

import json
from pathlib import Path

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.crear_plan_patch_desde_blueprints import CrearPlanPatchDesdeBlueprints
from aplicacion.puertos.blueprint import Blueprint, RepositorioBlueprints
from infraestructura.manifest_en_disco import LectorManifestEnDisco
from dominio.modelos import ArchivoGenerado, EspecificacionClase, EspecificacionProyecto, PlanGeneracion


class BlueprintEntidadMinimo(Blueprint):
    def nombre(self) -> str:
        return "crud_json"

    def version(self) -> str:
        return "1.0.0"

    def validar(self, especificacion: EspecificacionProyecto) -> None:
        especificacion.validar()

    def generar_plan(self, especificacion: EspecificacionProyecto) -> PlanGeneracion:
        archivos: list[ArchivoGenerado] = []
        for clase in especificacion.clases:
            nombre = clase.nombre.lower()
            archivos.append(ArchivoGenerado(f"dominio/entidades/{nombre}.py", "# entidad"))
            archivos.append(ArchivoGenerado(f"tests/aplicacion/test_crud_{nombre}.py", "# test"))
        return PlanGeneracion(archivos)


class RepoBlueprintFalso(RepositorioBlueprints):
    def listar_blueprints(self) -> list[Blueprint]:
        return [BlueprintEntidadMinimo()]

    def obtener_por_nombre(self, nombre: str) -> Blueprint:
        if nombre != "crud_json":
            raise ValueError("No encontrado")
        return BlueprintEntidadMinimo()


def test_patch_nueva_clase_genera_solo_producto(tmp_path: Path) -> None:
    manifest = {
        "version_generador": "0.7.0",
        "blueprints_usados": ["crud_json@1.0.0"],
        "archivos": [
            {"ruta_relativa": "dominio/entidades/cliente.py", "hash_sha256": "hash-cliente"},
        ],
        "timestamp_generacion": "2026-01-01T00:00:00+00:00",
        "opciones": {"origen": "test"},
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    especificacion = EspecificacionProyecto(
        nombre_proyecto="demo",
        ruta_destino=str(tmp_path),
        version="0.7.0",
        clases=[EspecificacionClase(nombre="Producto")],
    )

    caso_uso = CrearPlanPatchDesdeBlueprints(
        lector_manifest=LectorManifestEnDisco(),
        crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepoBlueprintFalso()),
    )

    plan = caso_uso.ejecutar(especificacion, str(tmp_path))

    assert plan.obtener_rutas() == [
        "dominio/entidades/producto.py",
        "tests/aplicacion/test_crud_producto.py",
    ]

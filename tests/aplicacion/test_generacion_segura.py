"""Pruebas de robustez para generación segura de proyectos MVP."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import (
    GenerarProyectoMvp,
    GenerarProyectoMvpEntrada,
)
from dominio.excepciones.proyecto_ya_existe_error import ProyectoYaExisteError
from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.sistema_archivos_real import SistemaArchivosReal


class EjecutarPlanFalla:
    def ejecutar(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("fallo interno simulado")


def _entrada(tmp_path: Path) -> GenerarProyectoMvpEntrada:
    especificacion = EspecificacionProyecto(
        nombre_proyecto="proyecto_seguro",
        ruta_destino=str(tmp_path),
        descripcion="Proyecto de pruebas",
        version="1.0.0",
    )
    clase = EspecificacionClase(nombre="Cliente")
    clase.agregar_atributo(EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True))
    especificacion.agregar_clase(clase)

    return GenerarProyectoMvpEntrada(
        especificacion_proyecto=especificacion,
        ruta_destino=str(tmp_path),
        nombre_proyecto="proyecto_seguro",
        blueprints=["base_clean_arch_v1", "crud_json_v1"],
    )


def test_generacion_normal_crea_manifest_configuracion(tmp_path: Path) -> None:
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco("blueprints")),
        ejecutar_plan=EjecutarPlan(SistemaArchivosReal()),
        sistema_archivos=SistemaArchivosReal(),
    )

    salida = caso_uso.ejecutar(_entrada(tmp_path))

    assert salida.valido is True
    ruta_manifest = tmp_path / "proyecto_seguro" / "configuracion" / "MANIFEST.json"
    assert ruta_manifest.exists()
    payload = json.loads(ruta_manifest.read_text(encoding="utf-8"))
    assert payload["blueprints"] == ["base_clean_arch_v1", "crud_json_v1"]


def test_carpeta_existente_no_vacia_lanza_proyecto_ya_existe_error(tmp_path: Path) -> None:
    ruta_proyecto = tmp_path / "proyecto_seguro"
    ruta_proyecto.mkdir(parents=True)
    (ruta_proyecto / "previo.txt").write_text("contenido", encoding="utf-8")

    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco("blueprints")),
        ejecutar_plan=EjecutarPlan(SistemaArchivosReal()),
        sistema_archivos=SistemaArchivosReal(),
    )

    with pytest.raises(ProyectoYaExisteError):
        caso_uso.ejecutar(_entrada(tmp_path))


def test_rollback_elimina_carpeta_cuando_hay_fallo_interno(tmp_path: Path) -> None:
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco("blueprints")),
        ejecutar_plan=EjecutarPlanFalla(),
        sistema_archivos=SistemaArchivosReal(),
    )

    salida = caso_uso.ejecutar(_entrada(tmp_path))

    assert salida.valido is False
    assert not (tmp_path / "proyecto_seguro").exists()

"""Test de integración completo para la generación MVP."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import (
    GenerarProyectoMvp,
    GenerarProyectoMvpEntrada,
)
from aplicacion.casos_uso.generar_manifest import GenerarManifest
from dominio.excepciones.proyecto_ya_existe_error import ProyectoYaExisteError
from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto
from infraestructura.calculadora_hash_real import CalculadoraHashReal
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.sistema_archivos_real import SistemaArchivosReal


DIRECTORIOS_OBLIGATORIOS = [
    "dominio",
    "aplicacion",
    "infraestructura",
    "presentacion",
    "tests",
    "docs",
    "logs",
    "configuracion",
    "scripts",
]


ARCHIVOS_CLAVE = [
    "VERSION",
    "CHANGELOG.md",
    "requirements.txt",
    "configuracion/MANIFEST.json",
]


BLUEPRINTS_MVP = ["base_clean_arch_v1", "crud_json_v1"]


def _crear_caso_uso() -> GenerarProyectoMvp:
    sistema_archivos = SistemaArchivosReal()
    return GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco("blueprints")),
        ejecutar_plan=EjecutarPlan(sistema_archivos, GenerarManifest(CalculadoraHashReal())),
        sistema_archivos=sistema_archivos,
    )


def _crear_especificacion(ruta_base: Path, nombre_proyecto: str) -> EspecificacionProyecto:
    especificacion = EspecificacionProyecto(
        nombre_proyecto=nombre_proyecto,
        ruta_destino=str(ruta_base),
        descripcion="Proyecto de integración MVP",
        version="1.0.0",
    )
    clase = EspecificacionClase(nombre="Cliente")
    clase.agregar_atributo(EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True))
    clase.agregar_atributo(EspecificacionAtributo(nombre="edad", tipo="int", obligatorio=False))
    especificacion.agregar_clase(clase)
    return especificacion


def test_generacion_mvp_completa_valida_manifest_y_auditoria(tmp_path: Path) -> None:
    caso_uso = _crear_caso_uso()
    especificacion = _crear_especificacion(tmp_path, "proyecto_integracion")

    salida = caso_uso.ejecutar(
        GenerarProyectoMvpEntrada(
            especificacion_proyecto=especificacion,
            ruta_destino=str(tmp_path),
            nombre_proyecto="proyecto_integracion",
            blueprints=BLUEPRINTS_MVP,
        )
    )

    ruta_proyecto = Path(salida.ruta_generada)
    assert ruta_proyecto.exists()
    assert ruta_proyecto.is_dir()

    for directorio in DIRECTORIOS_OBLIGATORIOS:
        assert (ruta_proyecto / directorio).is_dir()

    for archivo in ARCHIVOS_CLAVE:
        assert (ruta_proyecto / archivo).is_file()

    contenido_manifest = (ruta_proyecto / "configuracion" / "MANIFEST.json").read_text(encoding="utf-8")
    manifest = json.loads(contenido_manifest)
    assert manifest["blueprints"] == BLUEPRINTS_MVP
    assert manifest["clases"] == [{"nombre": "Cliente", "atributos": ["nombre", "edad"]}]
    assert manifest["archivos_generados"] > 0

    auditor = AuditarProyectoGenerado(ejecutar_pytest=False)
    resultado = auditor.auditar(str(ruta_proyecto))
    assert resultado.valido is True
    assert resultado.errores == []


def test_generacion_mvp_hace_rollback_si_falla_plan(tmp_path: Path) -> None:
    caso_uso = _crear_caso_uso()
    nombre_proyecto = "proyecto_con_fallo"
    ruta_proyecto = tmp_path / nombre_proyecto
    especificacion = _crear_especificacion(tmp_path, nombre_proyecto)

    salida = caso_uso.ejecutar(
        GenerarProyectoMvpEntrada(
            especificacion_proyecto=especificacion,
            ruta_destino=str(tmp_path),
            nombre_proyecto=nombre_proyecto,
            blueprints=["base_clean_arch_v1", "blueprint_inexistente_v1"],
        )
    )

    assert salida.valido is False
    assert salida.errores
    assert not ruta_proyecto.exists()


def test_generacion_mvp_falla_si_destino_no_vacio_sin_modificarlo(tmp_path: Path) -> None:
    caso_uso = _crear_caso_uso()
    nombre_proyecto = "proyecto_existente"
    ruta_proyecto = tmp_path / nombre_proyecto
    ruta_proyecto.mkdir(parents=True, exist_ok=False)
    marcador = ruta_proyecto / "marcador.txt"
    marcador.write_text("contenido_original", encoding="utf-8")

    especificacion = _crear_especificacion(tmp_path, nombre_proyecto)

    with pytest.raises(ProyectoYaExisteError):
        caso_uso.ejecutar(
            GenerarProyectoMvpEntrada(
                especificacion_proyecto=especificacion,
                ruta_destino=str(tmp_path),
                nombre_proyecto=nombre_proyecto,
                blueprints=BLUEPRINTS_MVP,
            )
        )

    assert ruta_proyecto.exists()
    assert marcador.exists()
    assert marcador.read_text(encoding="utf-8") == "contenido_original"
    assert list(ruta_proyecto.iterdir()) == [marcador]

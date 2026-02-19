"""Pruebas del pipeline de GenerarProyectoMvp."""

from __future__ import annotations

from pathlib import Path

import pytest

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import (
    GenerarProyectoMvp,
    GenerarProyectoMvpEntrada,
)
from aplicacion.errores import ErrorGeneracionProyecto
from dominio.modelos import ArchivoGenerado, EspecificacionProyecto, PlanGeneracion


class CrearPlanFalso:
    def ejecutar(self, especificacion: EspecificacionProyecto, nombres_blueprints: list[str]) -> PlanGeneracion:
        return PlanGeneracion([ArchivoGenerado("README.md", "ok")])


class EjecutarPlanFalso:
    def __init__(self) -> None:
        self.llamadas = 0

    def ejecutar(self, **kwargs):  # type: ignore[no-untyped-def]
        self.llamadas += 1
        return ["README.md", "VERSION"]


class SistemaArchivosFalso:
    def __init__(self, falla: bool = False) -> None:
        self.falla = falla
        self.directorios: list[str] = []

    def asegurar_directorio(self, ruta: str) -> None:
        if self.falla:
            raise OSError("fallo preparando estructura")
        self.directorios.append(ruta)


class GeneradorManifestFalso:
    def __init__(self, falla: bool = False) -> None:
        self.falla = falla
        self.llamadas = 0

    def generar(self, **kwargs):  # type: ignore[no-untyped-def]
        self.llamadas += 1
        if self.falla:
            raise RuntimeError("fallo publicando manifest")


class AuditorFalso:
    def __init__(self, falla: bool = False) -> None:
        self.falla = falla

    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        if self.falla:
            raise RuntimeError("fallo auditoria")
        return ResultadoAuditoria(errores=[], warnings=[])


def _entrada(tmp_path: Path) -> GenerarProyectoMvpEntrada:
    return GenerarProyectoMvpEntrada(
        especificacion_proyecto=EspecificacionProyecto(
            nombre_proyecto="demo",
            ruta_destino=str(tmp_path),
            descripcion="Proyecto demo",
            version="1.0.0",
        ),
        ruta_destino=str(tmp_path),
        nombre_proyecto="demo",
        blueprints=["base_clean_arch_v1"],
    )


def test_happy_path_completo(tmp_path: Path) -> None:
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(),
        ejecutar_plan=EjecutarPlanFalso(),
        sistema_archivos=SistemaArchivosFalso(),
        generador_manifest=GeneradorManifestFalso(),
        auditor=AuditorFalso(),
    )

    salida = caso_uso.ejecutar(_entrada(tmp_path))

    assert salida.valido is True
    assert salida.archivos_generados == 2


def test_falla_preparar_estructura_ejecuta_rollback(tmp_path: Path) -> None:
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(),
        ejecutar_plan=EjecutarPlanFalso(),
        sistema_archivos=SistemaArchivosFalso(falla=True),
        generador_manifest=GeneradorManifestFalso(),
        auditor=AuditorFalso(),
    )

    with pytest.raises(ErrorGeneracionProyecto):
        caso_uso.ejecutar(_entrada(tmp_path))

    assert not (tmp_path / "demo").exists()


def test_falla_publicar_manifest_ejecuta_rollback(tmp_path: Path) -> None:
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(),
        ejecutar_plan=EjecutarPlanFalso(),
        sistema_archivos=SistemaArchivosFalso(),
        generador_manifest=GeneradorManifestFalso(falla=True),
        auditor=AuditorFalso(),
    )

    with pytest.raises(ErrorGeneracionProyecto):
        caso_uso.ejecutar(_entrada(tmp_path))

    assert not (tmp_path / "demo").exists()


def test_falla_auditoria_ejecuta_rollback(tmp_path: Path) -> None:
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(),
        ejecutar_plan=EjecutarPlanFalso(),
        sistema_archivos=SistemaArchivosFalso(),
        generador_manifest=GeneradorManifestFalso(),
        auditor=AuditorFalso(falla=True),
    )

    with pytest.raises(ErrorGeneracionProyecto):
        caso_uso.ejecutar(_entrada(tmp_path))

    assert not (tmp_path / "demo").exists()


def test_no_mutar_entrada_original(tmp_path: Path) -> None:
    entrada = _entrada(tmp_path)
    nombre_original = entrada.especificacion_proyecto.nombre_proyecto
    ruta_original = entrada.especificacion_proyecto.ruta_destino

    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(),
        ejecutar_plan=EjecutarPlanFalso(),
        sistema_archivos=SistemaArchivosFalso(),
        generador_manifest=GeneradorManifestFalso(),
        auditor=AuditorFalso(),
    )

    caso_uso.ejecutar(entrada)

    assert entrada.especificacion_proyecto.nombre_proyecto == nombre_original
    assert entrada.especificacion_proyecto.ruta_destino == ruta_original


def test_caso_limite_entrada_minima_valida(tmp_path: Path) -> None:
    entrada = GenerarProyectoMvpEntrada(
        especificacion_proyecto=EspecificacionProyecto(
            nombre_proyecto="m",
            ruta_destino=str(tmp_path),
        ),
        ruta_destino=str(tmp_path),
        nombre_proyecto="m",
        blueprints=[],
    )
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(),
        ejecutar_plan=EjecutarPlanFalso(),
        sistema_archivos=SistemaArchivosFalso(),
        generador_manifest=GeneradorManifestFalso(),
        auditor=AuditorFalso(),
    )

    salida = caso_uso.ejecutar(entrada)

    assert salida.valido is True
    assert salida.ruta_generada.endswith("/m")

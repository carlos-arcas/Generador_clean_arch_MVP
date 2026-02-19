from __future__ import annotations

import pytest

from pathlib import Path

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import (
    GenerarProyectoMvp,
    GenerarProyectoMvpEntrada,
)
from aplicacion.casos_uso.generacion.pasos.errores_pipeline import ErrorPublicacionManifestGeneracion
from dominio.modelos import ArchivoGenerado, EspecificacionProyecto, PlanGeneracion


class CrearPlanFalso:
    def __init__(self, plan: PlanGeneracion | None = None) -> None:
        self._plan = plan or PlanGeneracion([ArchivoGenerado("README.md", "ok")])

    def ejecutar(self, especificacion: EspecificacionProyecto, nombres_blueprints: list[str]) -> PlanGeneracion:
        return self._plan


class EjecutarPlanFalso:
    def __init__(self, salida: list[str] | None = None, error: Exception | None = None) -> None:
        self._salida = ["README.md"] if salida is None else salida
        self._error = error

    def ejecutar(self, **kwargs):  # type: ignore[no-untyped-def]
        if self._error is not None:
            raise self._error
        return self._salida


class SistemaArchivosFalso:
    def __init__(self) -> None:
        self.directorios: list[str] = []

    def asegurar_directorio(self, ruta: str) -> None:
        self.directorios.append(ruta)


class GeneradorManifestFalso:
    def __init__(self) -> None:
        self.llamadas = 0

    def generar(self, ruta_proyecto: str, especificacion_proyecto, blueprints, archivos_generados) -> None:  # type: ignore[no-untyped-def]
        self.llamadas += 1


class AuditorFalso:
    def __init__(self, valido: bool = True) -> None:
        self._valido = valido

    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        if self._valido:
            return ResultadoAuditoria(errores=[], warnings=[])
        return ResultadoAuditoria(errores=["error"], warnings=[])


def _entrada(tmp_path: Path, blueprints: list[str] | None = None) -> GenerarProyectoMvpEntrada:
    return GenerarProyectoMvpEntrada(
        especificacion_proyecto=EspecificacionProyecto("demo", str(tmp_path)),
        ruta_destino=str(tmp_path),
        nombre_proyecto="demo",
        blueprints=blueprints or ["base_clean_arch_v1"],
    )


def test_generar_proyecto_mvp_ok_con_puertos(tmp_path: Path) -> None:
    sistema = SistemaArchivosFalso()
    manifest = GeneradorManifestFalso()
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(),
        ejecutar_plan=EjecutarPlanFalso(["README.md", "VERSION"]),
        sistema_archivos=sistema,
        generador_manifest=manifest,
        auditor=AuditorFalso(),
    )

    salida = caso_uso.ejecutar(_entrada(tmp_path))

    assert salida.valido is True
    assert salida.archivos_generados == 2
    assert manifest.llamadas == 1


def test_generar_proyecto_mvp_error_si_falla_puerto_manifest(tmp_path: Path) -> None:
    class GeneradorManifestFalla:
        def generar(self, **kwargs):  # type: ignore[no-untyped-def]
            raise RuntimeError("manifest roto")

    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(),
        ejecutar_plan=EjecutarPlanFalso(),
        sistema_archivos=SistemaArchivosFalso(),
        generador_manifest=GeneradorManifestFalla(),
        auditor=AuditorFalso(),
    )

    with pytest.raises(ErrorPublicacionManifestGeneracion):
        caso_uso.ejecutar(_entrada(tmp_path))


def test_generar_proyecto_mvp_limite_blueprints_vacios(tmp_path: Path) -> None:
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(PlanGeneracion()),
        ejecutar_plan=EjecutarPlanFalso([]),
        sistema_archivos=SistemaArchivosFalso(),
        generador_manifest=GeneradorManifestFalso(),
        auditor=AuditorFalso(),
    )

    salida = caso_uso.ejecutar(_entrada(tmp_path, blueprints=[]))

    assert salida.valido is True
    assert salida.archivos_generados == 0

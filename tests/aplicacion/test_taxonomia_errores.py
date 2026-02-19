"""Pruebas de taxonomía y propagación de errores por capa."""

from __future__ import annotations

from pathlib import Path

import pytest

from aplicacion.casos_uso.generacion.generar_proyecto_mvp import (
    GenerarProyectoMvp,
    GenerarProyectoMvpEntrada,
)
from aplicacion.errores import ErrorGeneracionProyecto
from dominio.errores import ErrorDominio, ErrorInvarianteDominio
from dominio.especificacion import EspecificacionProyecto
from infraestructura.errores import ErrorFilesystem


class CrearPlanFalso:
    def ejecutar(self, especificacion: EspecificacionProyecto, blueprints: list[str]) -> object:  # noqa: ARG002
        return object()


class EjecutarPlanFalso:
    def ejecutar(self, **kwargs):  # type: ignore[no-untyped-def]
        return []


class SistemaArchivosOk:
    def asegurar_directorio(self, ruta_absoluta: str) -> None:  # noqa: ARG002
        return None


class GeneradorManifestOk:
    def generar(self, **kwargs):  # type: ignore[no-untyped-def]
        return {"ok": True}


class AuditorFallaInfra:
    def auditar(self, ruta_proyecto: str):  # noqa: ARG002
        raise ErrorFilesystem("No fue posible escribir en disco.")


class AuditorFallaDominio:
    def auditar(self, ruta_proyecto: str):  # noqa: ARG002
        raise ErrorInvarianteDominio("Invariante de dominio inválida.")



def _entrada(tmp_path: Path) -> GenerarProyectoMvpEntrada:
    return GenerarProyectoMvpEntrada(
        especificacion_proyecto=EspecificacionProyecto(
            nombre_proyecto="demo",
            ruta_destino=str(tmp_path),
            version="1.0.0",
        ),
        ruta_destino=str(tmp_path),
        nombre_proyecto="demo",
        blueprints=["base_clean_arch_v1"],
    )


def test_error_infraestructura_se_envuelve_en_error_generacion(tmp_path: Path) -> None:
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(),
        ejecutar_plan=EjecutarPlanFalso(),
        sistema_archivos=SistemaArchivosOk(),
        generador_manifest=GeneradorManifestOk(),
        auditor=AuditorFallaInfra(),
    )

    with pytest.raises(ErrorGeneracionProyecto):
        caso_uso.ejecutar(_entrada(tmp_path))


def test_error_generacion_preserva_causa_original(tmp_path: Path) -> None:
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(),
        ejecutar_plan=EjecutarPlanFalso(),
        sistema_archivos=SistemaArchivosOk(),
        generador_manifest=GeneradorManifestOk(),
        auditor=AuditorFallaInfra(),
    )

    with pytest.raises(ErrorGeneracionProyecto) as exc_info:
        caso_uso.ejecutar(_entrada(tmp_path))

    assert isinstance(exc_info.value.__cause__, ErrorFilesystem)


def test_error_dominio_no_se_convierte_en_error_tecnico(tmp_path: Path) -> None:
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanFalso(),
        ejecutar_plan=EjecutarPlanFalso(),
        sistema_archivos=SistemaArchivosOk(),
        generador_manifest=GeneradorManifestOk(),
        auditor=AuditorFallaDominio(),
    )

    with pytest.raises(ErrorDominio):
        caso_uso.ejecutar(_entrada(tmp_path))


def test_no_hay_except_exception_en_casos_uso_criticos() -> None:
    rutas = [
        Path("aplicacion/casos_uso/generacion"),
        Path("aplicacion/casos_uso/auditoria"),
    ]
    encontrados: list[str] = []
    for ruta in rutas:
        for archivo in ruta.rglob("*.py"):
            contenido = archivo.read_text(encoding="utf-8")
            if "except Exception" in contenido:
                encontrados.append(archivo.as_posix())

    assert encontrados == []

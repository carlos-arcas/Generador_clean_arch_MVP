from __future__ import annotations

import logging
from pathlib import Path

import pytest

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp, GenerarProyectoMvpEntrada
from aplicacion.errores import ErrorGeneracionProyecto
from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto
from infraestructura.logging_config import configurar_logging
from infraestructura.manifest.generador_manifest import GeneradorManifest
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.sistema_archivos_real import SistemaArchivosReal


class _SistemaArchivosConPermisoDenegado(SistemaArchivosReal):
    def asegurar_directorio(self, ruta: str) -> None:
        raise PermissionError(f"denegado: {ruta}")


class _ManifestConError(GeneradorManifest):
    def generar(self, **kwargs):
        del kwargs
        raise OSError("disco lleno")


def _crear_especificacion(ruta_base: Path, nombre_proyecto: str) -> EspecificacionProyecto:
    especificacion = EspecificacionProyecto(nombre_proyecto=nombre_proyecto, ruta_destino=str(ruta_base), version="1.0.0")
    clase = EspecificacionClase(nombre="Cliente")
    clase.agregar_atributo(EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True))
    especificacion.agregar_clase(clase)
    return especificacion


def _crear_generador(sistema_archivos=None, manifest=None) -> GenerarProyectoMvp:
    sistema = sistema_archivos or SistemaArchivosReal()
    return GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco("blueprints")),
        ejecutar_plan=EjecutarPlan(sistema),
        sistema_archivos=sistema,
        generador_manifest=manifest or GeneradorManifest(),
    )


def _estado_relativo(base: Path) -> set[str]:
    if not base.exists():
        return set()
    return {str(path.relative_to(base)) for path in base.rglob("*")}


@pytest.mark.parametrize(
    ("caso", "generador"),
    [
        ("permiso_denegado", lambda: _crear_generador(sistema_archivos=_SistemaArchivosConPermisoDenegado())),
        ("manifest_error", lambda: _crear_generador(manifest=_ManifestConError())),
    ],
)
def test_fallos_hostiles_hacen_rollback_sin_huerfanos_y_con_stacktrace(
    tmp_path: Path,
    capsys,
    caso: str,
    generador,
) -> None:
    logs_dir = tmp_path / "logs"
    configurar_logging(str(logs_dir))

    ruta_proyecto = tmp_path / caso
    estado_prev = _estado_relativo(ruta_proyecto)

    with pytest.raises(ErrorGeneracionProyecto):
        try:
            generador().ejecutar(
                GenerarProyectoMvpEntrada(
                    especificacion_proyecto=_crear_especificacion(tmp_path, caso),
                    ruta_destino=str(tmp_path),
                    nombre_proyecto=caso,
                    blueprints=["base_clean_arch_v1"],
                )
            )
        except ErrorGeneracionProyecto:
            logging.getLogger("hostil").exception("caso_uso=GenerarProyectoMvp hostil=%s", caso)
            raise

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    estado_post = _estado_relativo(ruta_proyecto)
    assert (not ruta_proyecto.exists()) or (not estado_post) or (estado_post == estado_prev)

    huerfanos = estado_post - estado_prev
    assert not huerfanos

    seguimiento = (logs_dir / "seguimiento.log").read_text(encoding="utf-8")
    crashes = (logs_dir / "crashes.log").read_text(encoding="utf-8")
    assert "INFO" in seguimiento
    assert "caso_uso=GenerarProyectoMvp" in seguimiento
    assert "Traceback" in crashes


def test_fallo_hostil_sobre_directorio_preexistente_no_deja_huerfanos(tmp_path: Path) -> None:
    ruta_proyecto = tmp_path / "preexistente"
    ruta_proyecto.mkdir()
    estado_prev = _estado_relativo(ruta_proyecto)

    with pytest.raises(ErrorGeneracionProyecto):
        _crear_generador(manifest=_ManifestConError()).ejecutar(
            GenerarProyectoMvpEntrada(
                especificacion_proyecto=_crear_especificacion(tmp_path, "preexistente"),
                ruta_destino=str(tmp_path),
                nombre_proyecto="preexistente",
                blueprints=["base_clean_arch_v1"],
            )
        )

    estado_post = _estado_relativo(ruta_proyecto)
    assert (not ruta_proyecto.exists()) or (not estado_post) or (estado_post == estado_prev)
    assert not (estado_post - estado_prev)

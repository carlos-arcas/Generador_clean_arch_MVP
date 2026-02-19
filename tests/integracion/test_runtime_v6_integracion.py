"""Auditoría runtime v6: integración E2E, fallos hostiles y concurrencia básica."""

from __future__ import annotations

import copy
import json
import logging
from pathlib import Path
import threading

import pytest

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp, GenerarProyectoMvpEntrada
from aplicacion.casos_uso.presets.cargar_preset_proyecto import CargarPresetProyecto
from aplicacion.errores import ErrorGeneracionProyecto, ErrorValidacion
from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto
from infraestructura.logging_config import configurar_logging
from infraestructura.manifest.generador_manifest import GeneradorManifest
from infraestructura.presets.repositorio_presets_json import RepositorioPresetsJson
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.sistema_archivos_real import SistemaArchivosReal
from presentacion.wizard.dtos import DatosWizardProyecto
from presentacion.wizard.orquestadores.orquestador_finalizacion_wizard import (
    DtoEntradaFinalizacionWizard,
    OrquestadorFinalizacionWizard,
)


def _crear_especificacion(ruta_base: Path, nombre_proyecto: str) -> EspecificacionProyecto:
    especificacion = EspecificacionProyecto(
        nombre_proyecto=nombre_proyecto,
        ruta_destino=str(ruta_base),
        descripcion="Proyecto runtime",
        version="1.0.0",
    )
    clase = EspecificacionClase(nombre="Cliente")
    clase.agregar_atributo(EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True))
    especificacion.agregar_clase(clase)
    return especificacion


def _crear_generador(sistema_archivos: SistemaArchivosReal | object | None = None, manifest: object | None = None):
    sistema = sistema_archivos or SistemaArchivosReal()
    return GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco("blueprints")),
        ejecutar_plan=EjecutarPlan(sistema),
        sistema_archivos=sistema,
        generador_manifest=manifest if manifest is not None else GeneradorManifest(),
    )


def test_e2e_generacion_completa_manifest_auditoria_y_rollback_limpio(tmp_path: Path) -> None:
    caso_uso = _crear_generador()
    especificacion = _crear_especificacion(tmp_path, "runtime_ok")
    entrada = GenerarProyectoMvpEntrada(especificacion, str(tmp_path), "runtime_ok", ["base_clean_arch_v1", "crud_json_v1"])

    salida = caso_uso.ejecutar(entrada)

    ruta_proyecto = Path(salida.ruta_generada)
    assert (ruta_proyecto / "configuracion" / "MANIFEST.json").exists()
    manifest = json.loads((ruta_proyecto / "configuracion" / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["blueprints"] == ["base_clean_arch_v1", "crud_json_v1"]

    resultado_auditoria = AuditarProyectoGenerado().auditar(str(ruta_proyecto))
    assert resultado_auditoria.valido is True

    with pytest.raises(ErrorGeneracionProyecto):
        caso_uso.ejecutar(
            GenerarProyectoMvpEntrada(
                _crear_especificacion(tmp_path, "runtime_fallo"),
                str(tmp_path),
                "runtime_fallo",
                ["base_clean_arch_v1", "blueprint_inexistente_v1"],
            )
        )
    assert not (tmp_path / "runtime_fallo").exists()



def test_wizard_orquestador_integra_y_no_muta_dto() -> None:
    proyecto = EspecificacionProyecto(nombre_proyecto="demo", ruta_destino="/tmp/demo")
    datos = DatosWizardProyecto(
        nombre="demo",
        ruta="/tmp/demo",
        descripcion="",
        version="1.0.0",
        proyecto=proyecto,
        persistencia="JSON",
    )
    dto = DtoEntradaFinalizacionWizard(datos_wizard=datos, blueprints=["base_clean_arch_v1"])
    dto_copia = copy.deepcopy(dto)
    entradas = []

    orquestador = OrquestadorFinalizacionWizard(
        validador_final=lambda p: p,
        lanzador_generacion=lambda entrada: entradas.append(entrada),
    )

    resultado = orquestador.finalizar(dto)

    assert resultado.exito is True
    assert entradas and entradas[0].blueprints == ["base_clean_arch_v1"]
    assert dto == dto_copia



def test_auditoria_integrada_detecta_violacion_de_capa(tmp_path: Path) -> None:
    base = tmp_path / "proyecto"
    for carpeta in ["dominio", "aplicacion", "infraestructura", "presentacion", "tests", "docs", "logs", "configuracion", "scripts"]:
        (base / carpeta).mkdir(parents=True, exist_ok=True)
    (base / "VERSION").write_text("1.0.0", encoding="utf-8")
    (base / "CHANGELOG.md").write_text("init", encoding="utf-8")
    (base / "requirements.txt").write_text("", encoding="utf-8")
    (base / "configuracion" / "MANIFEST.json").write_text("{}", encoding="utf-8")

    (base / "dominio" / "modelo.py").write_text("from infraestructura.repo import Repo\n", encoding="utf-8")

    resultado = AuditarProyectoGenerado().auditar(str(base))

    assert resultado.valido is False
    assert any("dominio" in err.lower() and "infraestructura" in err.lower() for err in resultado.errores)


class _SistemaArchivosPermissionError:
    def asegurar_directorio(self, ruta: str) -> None:
        raise PermissionError(f"denegado: {ruta}")


class _ManifestOSError:
    def generar(self, **_: object) -> None:
        raise OSError("disco lleno")


class _CasoUsoBloqueanteCancelado:
    def __init__(self, evento_cancelacion: threading.Event) -> None:
        self._evento = evento_cancelacion

    def ejecutar(self, _entrada: object):
        if self._evento.wait(timeout=0.2):
            raise OSError("cancelado por usuario")
        return object()


def test_fallos_hostiles_hacen_rollback_y_mensaje_coherente(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    generador_permiso = _crear_generador(sistema_archivos=_SistemaArchivosPermissionError())
    entrada_permiso = GenerarProyectoMvpEntrada(
        _crear_especificacion(tmp_path, "sin_permiso"),
        str(tmp_path),
        "sin_permiso",
        ["base_clean_arch_v1"],
    )
    with pytest.raises(ErrorGeneracionProyecto):
        generador_permiso.ejecutar(entrada_permiso)
    assert not (tmp_path / "sin_permiso").exists()

    generador_manifest_falla = _crear_generador(manifest=_ManifestOSError())
    entrada_manifest = GenerarProyectoMvpEntrada(
        _crear_especificacion(tmp_path, "fallo_manifest"),
        str(tmp_path),
        "fallo_manifest",
        ["base_clean_arch_v1"],
    )
    with pytest.raises(ErrorGeneracionProyecto) as error_manifest:
        generador_manifest_falla.ejecutar(entrada_manifest)
    assert "Falló la generación" in str(error_manifest.value)
    assert not (tmp_path / "fallo_manifest").exists()

    caplog.set_level(logging.WARNING)
    evento = threading.Event()
    worker = _CasoUsoBloqueanteCancelado(evento)
    evento.set()
    with pytest.raises(OSError):
        worker.ejecutar(object())



def test_preset_corrupto_y_blueprint_inexistente(tmp_path: Path) -> None:
    ruta_preset = tmp_path / "roto.json"
    ruta_preset.write_text("{ json", encoding="utf-8")

    cargar_preset = CargarPresetProyecto(RepositorioPresetsJson(str(tmp_path)))
    with pytest.raises(ErrorValidacion):
        cargar_preset.ejecutar(str(ruta_preset))

    caso_uso = _crear_generador()
    with pytest.raises(ErrorGeneracionProyecto):
        caso_uso.ejecutar(
            GenerarProyectoMvpEntrada(
                _crear_especificacion(tmp_path, "blueprint_missing"),
                str(tmp_path),
                "blueprint_missing",
                ["blueprint_que_no_existe"],
            )
        )
    assert not (tmp_path / "blueprint_missing").exists()



def test_logging_runtime_contiene_info_y_stacktrace(tmp_path: Path) -> None:
    configurar_logging(str(tmp_path))
    logger = logging.getLogger("runtime_v6")
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        logger.error("error hostil controlado", exc_info=True)
    logger.info("seguimiento de generación runtime")

    seguimiento = (tmp_path / "seguimiento.log").read_text(encoding="utf-8")
    crashes = (tmp_path / "crashes.log").read_text(encoding="utf-8")

    assert "seguimiento de generación runtime" in seguimiento
    assert "error hostil controlado" in crashes
    assert "Traceback" in crashes


def test_generaciones_consecutivas_no_comparten_estado_global(tmp_path: Path) -> None:
    caso_uso = _crear_generador()

    salida1 = caso_uso.ejecutar(
        GenerarProyectoMvpEntrada(
            _crear_especificacion(tmp_path, "consecutivo_a"),
            str(tmp_path),
            "consecutivo_a",
            ["base_clean_arch_v1"],
        )
    )
    salida2 = caso_uso.ejecutar(
        GenerarProyectoMvpEntrada(
            _crear_especificacion(tmp_path, "consecutivo_b"),
            str(tmp_path),
            "consecutivo_b",
            ["base_clean_arch_v1", "crud_json_v1"],
        )
    )

    assert Path(salida1.ruta_generada).name == "consecutivo_a"
    assert Path(salida2.ruta_generada).name == "consecutivo_b"
    assert Path(salida1.ruta_generada) != Path(salida2.ruta_generada)

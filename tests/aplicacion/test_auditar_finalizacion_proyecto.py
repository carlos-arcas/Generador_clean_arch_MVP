from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditar_finalizacion_proyecto import AuditarFinalizacionProyecto
from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionEntrada
from aplicacion.errores import ErrorConflictoArchivos
from aplicacion.puertos.ejecutor_procesos import ResultadoProceso
from dominio.especificacion import EspecificacionProyecto


class CrearPlanFalso:
    def __init__(self, conflicto: bool = False) -> None:
        self.conflicto = conflicto

    def ejecutar(self, especificacion: EspecificacionProyecto, nombres_blueprints: list[str]):
        if self.conflicto:
            raise ErrorConflictoArchivos("El plan contiene rutas duplicadas: ['presentacion/persona.py', 'tests/test_persona.py']")
        return object()


class GenerarMvpFalso:
    def __init__(self, falla: bool = False) -> None:
        self.falla = falla

    def ejecutar(self, entrada):  # type: ignore[no-untyped-def]
        ruta = Path(entrada.ruta_destino) / entrada.nombre_proyecto
        ruta.mkdir(parents=True, exist_ok=True)
        (ruta / "manifest.json").write_text("{}", encoding="utf-8")
        if self.falla:
            raise OSError("fallo manifest")


class AuditorArquitecturaFalso:
    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        return ResultadoAuditoria(errores=[], warnings=[])


class EjecutorProcesosFalso:
    def __init__(self) -> None:
        self.comandos: list[list[str]] = []

    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        self.comandos.append(comando)
        return ResultadoProceso(codigo_salida=0, stdout="ok", stderr="")


class SistemaArchivosRealControlado:
    def escribir_texto_atomico(self, ruta_absoluta: str, contenido: str) -> None:
        ruta = Path(ruta_absoluta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido, encoding="utf-8")

    def asegurar_directorio(self, ruta_absoluta: str) -> None:
        Path(ruta_absoluta).mkdir(parents=True, exist_ok=True)


def _crear_preset(tmp_path: Path, blueprints: list[str]) -> Path:
    ruta = tmp_path / "preset.json"
    ruta.write_text(
        """
{
  "nombre": "demo",
  "especificacion": {
    "nombre_proyecto": "Demo",
    "descripcion": "desc",
    "version": "1.0.0",
    "ruta_destino": "",
    "clases": []
  },
  "blueprints": [
"""
        + ",".join(f'    "{item}"' for item in blueprints)
        + """
  ],
  "metadata": {}
}
""",
        encoding="utf-8",
    )
    return ruta


def test_conflicto_preflight_falla_y_no_escribe_proyecto(tmp_path: Path) -> None:
    preset = _crear_preset(tmp_path, ["a", "b"])
    caso = AuditarFinalizacionProyecto(
        crear_plan_desde_blueprints=CrearPlanFalso(conflicto=True),
        generar_proyecto_mvp=GenerarMvpFalso(),
        auditor_arquitectura=AuditorArquitecturaFalso(),
        ejecutor_procesos=EjecutorProcesosFalso(),
        sistema_archivos=SistemaArchivosRealControlado(),
    )

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(
            ruta_preset=str(preset),
            ruta_salida_auditoria=str(tmp_path / "auditoria" / "manual"),
        )
    )

    etapa_preflight = next(etapa for etapa in salida.etapas if etapa.nombre.startswith("ETAPA 2"))
    assert etapa_preflight.estado == "FAIL"
    assert not (Path(salida.ruta_sandbox) / "Demo").exists()
    assert "rutas duplicadas" in salida.reporte_markdown.lower()


def test_camino_feliz_genera_manifest_y_smoke_pass(tmp_path: Path) -> None:
    preset = _crear_preset(tmp_path, ["base"])
    ejecutor = EjecutorProcesosFalso()
    caso = AuditarFinalizacionProyecto(
        crear_plan_desde_blueprints=CrearPlanFalso(conflicto=False),
        generar_proyecto_mvp=GenerarMvpFalso(),
        auditor_arquitectura=AuditorArquitecturaFalso(),
        ejecutor_procesos=ejecutor,
        sistema_archivos=SistemaArchivosRealControlado(),
    )

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(
            ruta_preset=str(preset),
            ruta_salida_auditoria=str(tmp_path / "auditoria" / "ok"),
        )
    )

    assert (Path(salida.ruta_sandbox) / "Demo" / "manifest.json").exists()
    assert any(etapa.estado == "PASS" for etapa in salida.etapas if etapa.nombre.startswith("ETAPA 3"))
    assert ejecutor.comandos[0] == ["python", "-m", "compileall", "."]


def test_fallo_manifest_en_etapa_3_reporta_stacktrace(tmp_path: Path) -> None:
    preset = _crear_preset(tmp_path, ["base"])
    caso = AuditarFinalizacionProyecto(
        crear_plan_desde_blueprints=CrearPlanFalso(conflicto=False),
        generar_proyecto_mvp=GenerarMvpFalso(falla=True),
        auditor_arquitectura=AuditorArquitecturaFalso(),
        ejecutor_procesos=EjecutorProcesosFalso(),
        sistema_archivos=SistemaArchivosRealControlado(),
    )

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(
            ruta_preset=str(preset),
            ruta_salida_auditoria=str(tmp_path / "auditoria" / "falla"),
        )
    )

    etapa_3 = next(etapa for etapa in salida.etapas if etapa.nombre.startswith("ETAPA 3"))
    assert etapa_3.estado == "FAIL"
    assert any("Traceback" in evidencia for evidencia in etapa_3.evidencia)

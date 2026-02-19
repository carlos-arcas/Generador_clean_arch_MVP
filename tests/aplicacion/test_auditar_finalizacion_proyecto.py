from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditar_finalizacion_proyecto import AuditarFinalizacionProyecto
from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionEntrada
from aplicacion.puertos.ejecutor_procesos import ResultadoProceso
from dominio.plan_generacion import ArchivoGenerado, PlanGeneracion


class CrearPlanFalso:
    def __init__(self, rutas_por_blueprint: dict[str, list[str]]) -> None:
        self.rutas_por_blueprint = rutas_por_blueprint

    def ejecutar(self, especificacion, nombres_blueprints):  # type: ignore[no-untyped-def]
        plan = PlanGeneracion()
        for ruta in self.rutas_por_blueprint[nombres_blueprints[0]]:
            plan.agregar_archivo(ArchivoGenerado(ruta_relativa=ruta, contenido_texto="x"))
        return plan


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


def _crear_preset(tmp_path: Path, blueprints: list[str]) -> Path:
    ruta = tmp_path / "preset.json"
    ruta.write_text(
        '{"nombre":"demo","especificacion":{"nombre_proyecto":"Demo","descripcion":"desc","version":"1.0.0","ruta_destino":"","clases":[]},"blueprints":'
        + str(blueprints).replace("'", '"')
        + ',"metadata":{}}',
        encoding="utf-8",
    )
    return ruta


def test_conflicto_preflight_falla_y_no_escribe_proyecto(tmp_path: Path) -> None:
    preset = _crear_preset(tmp_path, ["a", "b"])
    caso = AuditarFinalizacionProyecto(
        crear_plan_desde_blueprints=CrearPlanFalso({"a": ["x.py"], "b": ["x.py"]}),
        generar_proyecto_mvp=GenerarMvpFalso(),
        auditor_arquitectura=AuditorArquitecturaFalso(),
        ejecutor_procesos=EjecutorProcesosFalso(),
    )

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(
            ruta_preset=str(preset),
            ruta_salida_auditoria=str(tmp_path / "auditoria" / "manual"),
        )
    )

    assert any(etapa.nombre == "Preflight conflictos" and etapa.estado == "FAIL" for etapa in salida.etapas)
    assert salida.conflictos is not None
    assert not (Path(salida.ruta_sandbox) / "Demo").exists()


def test_camino_feliz_genera_manifest_y_smoke_pass(tmp_path: Path) -> None:
    preset = _crear_preset(tmp_path, ["base"])
    ejecutor = EjecutorProcesosFalso()
    caso = AuditarFinalizacionProyecto(
        crear_plan_desde_blueprints=CrearPlanFalso({"base": ["a.py"]}),
        generar_proyecto_mvp=GenerarMvpFalso(),
        auditor_arquitectura=AuditorArquitecturaFalso(),
        ejecutor_procesos=ejecutor,
    )

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(
            ruta_preset=str(preset),
            ruta_salida_auditoria=str(tmp_path / "auditoria" / "ok"),
        )
    )

    assert (Path(salida.ruta_sandbox) / "Demo" / "manifest.json").exists()
    assert any(etapa.estado == "PASS" for etapa in salida.etapas if etapa.nombre == "Generación sandbox")
    assert ejecutor.comandos[0] == ["python", "-m", "compileall", "."]

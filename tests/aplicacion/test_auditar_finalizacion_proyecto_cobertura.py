from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditar_finalizacion_proyecto import AuditarFinalizacionProyecto
from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionEntrada
from aplicacion.puertos.ejecutor_procesos import ResultadoProceso


class CrearPlanSimple:
    def ejecutar(self, especificacion, nombres_blueprints):  # type: ignore[no-untyped-def]
        from dominio.plan_generacion import ArchivoGenerado, PlanGeneracion

        plan = PlanGeneracion()
        plan.agregar_archivo(ArchivoGenerado(f"app/{nombres_blueprints[0]}.py", ""))
        return plan


class GeneradorFalla:
    def ejecutar(self, entrada):  # type: ignore[no-untyped-def]
        raise OSError("disk full")


class AuditorDummy:
    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        return ResultadoAuditoria(errores=[], warnings=[])


class EjecutorDummy:
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return ResultadoProceso(0, "ok", "")


class EjecutorCompileFail:
    def __init__(self) -> None:
        self.calls = 0

    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        self.calls += 1
        if self.calls == 1:
            return ResultadoProceso(1, "", "compile fail")
        return ResultadoProceso(0, "ok", "")


class GeneradorConManifest:
    def ejecutar(self, entrada):  # type: ignore[no-untyped-def]
        ruta = Path(entrada.ruta_destino) / entrada.nombre_proyecto
        ruta.mkdir(parents=True, exist_ok=True)
        (ruta / "manifest.json").write_text("{}", encoding="utf-8")


def test_carga_preset_inexistente_registra_fallo_io(tmp_path: Path) -> None:
    caso = AuditarFinalizacionProyecto(CrearPlanSimple(), GeneradorConManifest(), AuditorDummy(), EjecutorDummy())
    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(
            ruta_preset=str(tmp_path / "missing.json"),
            ruta_salida_auditoria=str(tmp_path / "sandbox"),
        )
    )
    etapa = next(et for et in salida.etapas if et.nombre == "Carga preset")
    assert etapa.estado == "FAIL"
    assert etapa.tipo_fallo == "IO"


def test_generacion_fallida_corta_pipeline(tmp_path: Path) -> None:
    preset = tmp_path / "preset.json"
    preset.write_text(
        '{"especificacion":{"nombre_proyecto":"Demo","descripcion":"","version":"1.0.0","clases":[{"nombre":"Persona","atributos":[]}]},"blueprints":["base"]}',
        encoding="utf-8",
    )
    caso = AuditarFinalizacionProyecto(CrearPlanSimple(), GeneradorFalla(), AuditorDummy(), EjecutorDummy())
    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(ruta_preset=str(preset), ruta_salida_auditoria=str(tmp_path / "sandbox"))
    )
    assert any(et.nombre == "Generación sandbox" and et.estado == "FAIL" for et in salida.etapas)
    assert any(et.nombre == "Smoke test" and et.estado == "SKIP" for et in salida.etapas)


def test_smoke_compileall_fail_clasifica_io(tmp_path: Path) -> None:
    preset = tmp_path / "preset.json"
    preset.write_text(
        '{"especificacion":{"nombre_proyecto":"Demo","descripcion":"","version":"1.0.0","clases":[{"nombre":"Persona","atributos":[]}]},"blueprints":["base"]}',
        encoding="utf-8",
    )
    caso = AuditarFinalizacionProyecto(CrearPlanSimple(), GeneradorConManifest(), AuditorDummy(), EjecutorCompileFail())
    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(ruta_preset=str(preset), ruta_salida_auditoria=str(tmp_path / "sandbox"))
    )
    etapa = next(et for et in salida.etapas if et.nombre == "Smoke test")
    assert etapa.estado == "FAIL"
    assert etapa.tipo_fallo == "IO"

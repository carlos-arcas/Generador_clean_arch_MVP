from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditar_finalizacion_proyecto import AuditarFinalizacionProyecto
from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionEntrada
from aplicacion.puertos.ejecutor_procesos import ResultadoProceso
from dominio.plan_generacion import ArchivoGenerado, PlanGeneracion


class CrearPlanDuplicado:
    def ejecutar(self, especificacion, nombres_blueprints):  # type: ignore[no-untyped-def]
        bp = nombres_blueprints[0]
        plan = PlanGeneracion()
        if bp == "bp_a":
            plan.agregar_archivo(ArchivoGenerado("app/persona.py", ""))
        if bp == "bp_b":
            plan.agregar_archivo(ArchivoGenerado("app/persona.py", ""))
        return plan


class GeneradorNulo:
    def ejecutar(self, entrada):  # type: ignore[no-untyped-def]
        raise AssertionError("No debe ejecutarse generación")


class AuditorNulo:
    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        return ResultadoAuditoria(errores=[], warnings=[])


class EjecutorNulo:
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return ResultadoProceso(0, "", "")


def test_preflight_detecta_blueprints_culpables(tmp_path: Path) -> None:
    preset = tmp_path / "preset.json"
    preset.write_text(
        '{"especificacion":{"nombre_proyecto":"Demo","descripcion":"","version":"1.0.0","clases":[]},"blueprints":["bp_a","bp_b"]}',
        encoding="utf-8",
    )
    caso = AuditarFinalizacionProyecto(CrearPlanDuplicado(), GeneradorNulo(), AuditorNulo(), EjecutorNulo())

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(ruta_preset=str(preset), ruta_salida_auditoria=str(tmp_path / "sandbox"))
    )

    assert salida.conflictos is not None
    assert salida.conflictos.rutas_por_blueprint["app/persona.py"] == ["bp_a", "bp_b"]

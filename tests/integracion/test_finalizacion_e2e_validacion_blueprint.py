from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditar_finalizacion_proyecto import AuditarFinalizacionProyecto
from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionEntrada, VALIDACION
from aplicacion.puertos.ejecutor_procesos import ResultadoProceso


class CrearPlanNoUsado:
    def ejecutar(self, especificacion, nombres_blueprints):  # type: ignore[no-untyped-def]
        raise AssertionError("No debe invocarse en fallo de validación")


class GeneradorNoUsado:
    def ejecutar(self, entrada):  # type: ignore[no-untyped-def]
        raise AssertionError("No debe invocarse en fallo de validación")


class AuditorNoUsado:
    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        raise AssertionError("No debe invocarse en fallo de validación")


class EjecutorNoUsado:
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        raise AssertionError("No debe invocarse en fallo de validación")


def test_finalizacion_preflight_validacion_blueprint_crud_json_sin_clases(tmp_path: Path) -> None:
    preset = tmp_path / "preset.json"
    preset.write_text(
        '{"especificacion":{"nombre_proyecto":"Demo","descripcion":"","version":"1.0.0","clases":[]},"blueprints":["crud_json"]}',
        encoding="utf-8",
    )
    caso = AuditarFinalizacionProyecto(CrearPlanNoUsado(), GeneradorNoUsado(), AuditorNoUsado(), EjecutorNoUsado())

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(ruta_preset=str(preset), ruta_salida_auditoria=str(tmp_path / "sandbox"))
    )

    etapa = next(et for et in salida.etapas if et.nombre == "Preflight validación entrada")
    assert etapa.estado == "FAIL"
    assert etapa.tipo_fallo == VALIDACION
    assert etapa.codigo == "VAL-001"
    assert "crud_json requiere al menos una clase" in (etapa.mensaje_usuario or "")

    from aplicacion.servicios.generador_informe_finalizacion_md import generar_markdown

    informe = generar_markdown(salida)
    assert "inesperado" not in informe.casefold()

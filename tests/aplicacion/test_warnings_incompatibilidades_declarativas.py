from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditar_finalizacion_proyecto import AuditarFinalizacionProyecto
from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionEntrada
from aplicacion.puertos.ejecutor_procesos import ResultadoProceso


class CrearPlanNoUsado:
    def ejecutar(self, especificacion, nombres_blueprints):  # type: ignore[no-untyped-def]
        raise AssertionError("No debe invocarse al fallar validación")


class GeneradorNoUsado:
    def ejecutar(self, entrada):  # type: ignore[no-untyped-def]
        raise AssertionError("No debe invocarse al fallar validación")


class AuditorNoUsado:
    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        raise AssertionError("No debe invocarse al fallar validación")


class EjecutorNoUsado:
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        raise AssertionError("No debe invocarse al fallar validación")


def test_warnings_incompatibilidades_declarativas_aparecen_ante_fallo_validacion(tmp_path: Path) -> None:
    preset = tmp_path / "preset_incompatible.json"
    preset.write_text(
        '{"especificacion":{"nombre_proyecto":"Demo","descripcion":"","version":"1.0.0","clases":[]},"blueprints":["crud_json","crud_sqlite"]}',
        encoding="utf-8",
    )
    caso = AuditarFinalizacionProyecto(CrearPlanNoUsado(), GeneradorNoUsado(), AuditorNoUsado(), EjecutorNoUsado())

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(ruta_preset=str(preset), ruta_salida_auditoria=str(tmp_path / "sandbox"))
    )

    evidencia = salida.evidencias["preflight_validacion_entrada"]
    assert "Warnings declarativos:" in evidencia
    assert "crud_json y crud_sqlite" in evidencia
    assert "elige 1 CRUD" in evidencia

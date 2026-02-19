from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditar_finalizacion_proyecto import AuditarFinalizacionProyecto
from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.dtos.auditoria import CONFLICTO, DtoAuditoriaFinalizacionEntrada
from aplicacion.puertos.ejecutor_procesos import ResultadoProceso
from dominio.plan_generacion import ArchivoGenerado, PlanGeneracion


class CrearPlanDuplicadoPersona:
    def ejecutar(self, especificacion, nombres_blueprints):  # type: ignore[no-untyped-def]
        plan = PlanGeneracion()
        bp = nombres_blueprints[0]
        if bp in {"crud_persona_a", "crud_persona_b"}:
            plan.agregar_archivo(ArchivoGenerado("aplicacion/persona.py", ""))
            plan.agregar_archivo(ArchivoGenerado("infraestructura/repositorio_persona.py", ""))
        return plan


class GeneradorNoUsado:
    def ejecutar(self, entrada):  # type: ignore[no-untyped-def]
        raise AssertionError("No debe invocarse cuando hay conflicto")


class AuditorNoUsado:
    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        raise AssertionError("No debe invocarse cuando hay conflicto")


class EjecutorNoUsado:
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        raise AssertionError("No debe invocarse cuando hay conflicto")


def test_finalizacion_preflight_conflicto_rutas_persona(tmp_path: Path) -> None:
    preset = tmp_path / "preset_conflicto_persona.json"
    preset.write_text(
        '{"especificacion":{"nombre_proyecto":"Demo","descripcion":"","version":"1.0.0","clases":[{"nombre":"Persona","atributos":[]}]},"blueprints":["crud_persona_a","crud_persona_b"]}',
        encoding="utf-8",
    )
    caso = AuditarFinalizacionProyecto(
        CrearPlanDuplicadoPersona(), GeneradorNoUsado(), AuditorNoUsado(), EjecutorNoUsado()
    )

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(ruta_preset=str(preset), ruta_salida_auditoria=str(tmp_path / "sandbox"))
    )

    etapa = next(et for et in salida.etapas if et.nombre == "Preflight conflictos de rutas")
    assert etapa.estado == "FAIL"
    assert etapa.tipo_fallo == CONFLICTO
    assert etapa.codigo == "CON-001"
    assert "ruta -> [blueprints]" in salida.evidencias.get("preflight_conflictos_rutas", "")

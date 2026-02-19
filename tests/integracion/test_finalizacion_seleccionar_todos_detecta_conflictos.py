from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditar_finalizacion_proyecto import AuditarFinalizacionProyecto
from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.dtos.auditoria import CONFLICTO, DtoAuditoriaFinalizacionEntrada
from aplicacion.puertos.ejecutor_procesos import ResultadoProceso
from dominio.plan_generacion import ArchivoGenerado, PlanGeneracion


class CrearPlanTodosBlueprints:
    BLUEPRINTS_DISPONIBLES = ("crud_json", "crud_sqlite", "api_fastapi")

    def ejecutar(self, especificacion, nombres_blueprints):  # type: ignore[no-untyped-def]
        blueprint = nombres_blueprints[0]
        plan = PlanGeneracion()
        if blueprint in {"crud_json", "crud_sqlite"}:
            plan.agregar_archivo(ArchivoGenerado("aplicacion/persona.py", ""))
            plan.agregar_archivo(ArchivoGenerado("infraestructura/repositorio_persona.py", ""))
        if blueprint == "api_fastapi":
            plan.agregar_archivo(ArchivoGenerado("presentacion/main.py", ""))
        return plan


class GeneradorNoDebeEjecutarse:
    def ejecutar(self, entrada):  # type: ignore[no-untyped-def]
        raise AssertionError("No debe llegar a fusionar/generar con conflictos")


class AuditorNoDebeEjecutarse:
    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        raise AssertionError("No debe auditar cuando el preflight falla")


class EjecutorNoDebeEjecutarse:
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        raise AssertionError("No debe ejecutar procesos cuando el preflight falla")


def _preset_seleccionar_todos(tmp_path: Path) -> Path:
    ruta = tmp_path / "preset_todos_blueprints.json"
    todos = list(CrearPlanTodosBlueprints.BLUEPRINTS_DISPONIBLES)
    ruta.write_text(
        '{"especificacion":{"nombre_proyecto":"Demo","descripcion":"","version":"1.0.0","clases":[{"nombre":"Persona","atributos":[]}]},"blueprints":'
        + str(todos).replace("'", '"')
        + "}",
        encoding="utf-8",
    )
    return ruta


def test_finalizacion_seleccionar_todos_detecta_conflictos(tmp_path: Path) -> None:
    caso = AuditarFinalizacionProyecto(
        CrearPlanTodosBlueprints(),
        GeneradorNoDebeEjecutarse(),
        AuditorNoDebeEjecutarse(),
        EjecutorNoDebeEjecutarse(),
    )

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(
            ruta_preset=str(_preset_seleccionar_todos(tmp_path)),
            ruta_salida_auditoria=str(tmp_path / "sandbox"),
        )
    )

    etapa_validacion = next(etapa for etapa in salida.etapas if etapa.nombre == "Preflight validación entrada")
    etapa_conflictos = next(etapa for etapa in salida.etapas if etapa.nombre == "Preflight conflictos de rutas")

    assert etapa_validacion.estado == "PASS"
    assert etapa_conflictos.estado == "FAIL"
    assert etapa_conflictos.tipo_fallo == CONFLICTO
    assert etapa_conflictos.codigo == "CON-001"
    evidencia = salida.evidencias["preflight_conflictos_rutas"]
    assert "total rutas duplicadas:" in evidencia
    assert "-> [" in evidencia

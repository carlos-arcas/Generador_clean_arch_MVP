from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditar_finalizacion_proyecto import AuditarFinalizacionProyecto
from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionEntrada
from aplicacion.errores import ErrorConflictoArchivos
from aplicacion.puertos.ejecutor_procesos import ResultadoProceso


class CrearPlanIntegracionDoble:
    def __init__(self, conflicto: bool) -> None:
        self.conflicto = conflicto

    def ejecutar(self, especificacion, nombres_blueprints):  # type: ignore[no-untyped-def]
        if self.conflicto:
            raise ErrorConflictoArchivos(
                "El plan contiene rutas duplicadas: ['aplicacion/persona.py', 'tests/test_persona.py', 'infraestructura/repo_persona.py']"
            )
        return object()


class GeneradorProyectoIntegracionDoble:
    def ejecutar(self, entrada):  # type: ignore[no-untyped-def]
        base = Path(entrada.ruta_destino) / entrada.nombre_proyecto
        (base / "tests").mkdir(parents=True, exist_ok=True)
        (base / "tests" / "test_demo.py").write_text("def test_demo():\n    assert True\n", encoding="utf-8")
        (base / "manifest.json").write_text("{}", encoding="utf-8")


class AuditorArquitecturaIntegracionDoble:
    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        return ResultadoAuditoria(errores=[], warnings=[])


class EjecutorProcesosIntegracionDoble:
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return ResultadoProceso(codigo_salida=0, stdout="ok", stderr="")


class SistemaArchivosIntegracionDoble:
    def escribir_texto_atomico(self, ruta_absoluta: str, contenido: str) -> None:
        ruta = Path(ruta_absoluta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido, encoding="utf-8")

    def asegurar_directorio(self, ruta_absoluta: str) -> None:
        Path(ruta_absoluta).mkdir(parents=True, exist_ok=True)


def _preset(tmp_path: Path) -> Path:
    ruta = tmp_path / "preset_e2e.json"
    ruta.write_text(
        '{"nombre":"x","especificacion":{"nombre_proyecto":"DemoE2E","descripcion":"d","version":"1.0.0","ruta_destino":"","clases":[]},"blueprints":["bp1","bp2"],"metadata":{}}',
        encoding="utf-8",
    )
    return ruta


def test_e2e_conflicto_duplicados_corta_antes_de_generar(tmp_path: Path) -> None:
    caso = AuditarFinalizacionProyecto(
        crear_plan_desde_blueprints=CrearPlanIntegracionDoble(conflicto=True),
        generar_proyecto_mvp=GeneradorProyectoIntegracionDoble(),
        auditor_arquitectura=AuditorArquitecturaIntegracionDoble(),
        ejecutor_procesos=EjecutorProcesosIntegracionDoble(),
        sistema_archivos=SistemaArchivosIntegracionDoble(),
    )

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(
            ruta_preset=str(_preset(tmp_path)),
            ruta_salida_auditoria=str(tmp_path / "sandbox" / "conflicto"),
        )
    )

    assert any(etapa.estado == "FAIL" for etapa in salida.etapas if etapa.nombre.startswith("ETAPA 2"))
    assert not (Path(salida.ruta_sandbox) / "DemoE2E").exists()
    assert "Conflictos detectados" in salida.reporte_markdown


def test_e2e_happy_path_genera_reporte(tmp_path: Path) -> None:
    caso = AuditarFinalizacionProyecto(
        crear_plan_desde_blueprints=CrearPlanIntegracionDoble(conflicto=False),
        generar_proyecto_mvp=GeneradorProyectoIntegracionDoble(),
        auditor_arquitectura=AuditorArquitecturaIntegracionDoble(),
        ejecutor_procesos=EjecutorProcesosIntegracionDoble(),
        sistema_archivos=SistemaArchivosIntegracionDoble(),
    )

    salida = caso.ejecutar(
        DtoAuditoriaFinalizacionEntrada(
            ruta_preset=str(_preset(tmp_path)),
            ruta_salida_auditoria=str(tmp_path / "sandbox" / "ok"),
        )
    )

    assert salida.exito_global is True
    assert Path(salida.ruta_reporte).exists()

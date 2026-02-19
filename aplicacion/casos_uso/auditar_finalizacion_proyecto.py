"""Caso de uso para auditar la finalización E2E de un proyecto generado."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import ast
import json
import logging
from pathlib import Path
import secrets
import tempfile
import traceback

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp, GenerarProyectoMvpEntrada
from aplicacion.dtos.auditoria import (
    DtoAuditoriaFinalizacionEntrada,
    DtoAuditoriaFinalizacionSalida,
    DtoEtapaAuditoria,
)
from aplicacion.errores import ErrorConflictoArchivos, ErrorValidacion
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos
from aplicacion.puertos.sistema_archivos import SistemaArchivos
from dominio.especificacion import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto

LOGGER = logging.getLogger(__name__)


@dataclass
class _ContextoEjecucion:
    id_ejecucion: str
    ruta_sandbox: Path
    ruta_reporte: Path


class AuditarFinalizacionProyecto:
    """Ejecuta un pipeline E2E de auditoría sobre un preset."""

    def __init__(
        self,
        crear_plan_desde_blueprints: CrearPlanDesdeBlueprints,
        generar_proyecto_mvp: GenerarProyectoMvp,
        auditor_arquitectura: AuditarProyectoGenerado,
        ejecutor_procesos: EjecutorProcesos,
        sistema_archivos: SistemaArchivos,
    ) -> None:
        self._crear_plan_desde_blueprints = crear_plan_desde_blueprints
        self._generar_proyecto_mvp = generar_proyecto_mvp
        self._auditor_arquitectura = auditor_arquitectura
        self._ejecutor_procesos = ejecutor_procesos
        self._sistema_archivos = sistema_archivos

    def ejecutar(self, entrada: DtoAuditoriaFinalizacionEntrada) -> DtoAuditoriaFinalizacionSalida:
        contexto = self._preparar_contexto(entrada)
        etapas: list[DtoEtapaAuditoria] = []
        LOGGER.info("[%s] Inicio auditoría finalización preset=%s", contexto.id_ejecucion, entrada.ruta_preset)

        preset, etapa_carga = self._cargar_preset(entrada.ruta_preset)
        etapas.append(etapa_carga)
        if etapa_carga.estado == "FAIL":
            return self._cerrar(contexto, etapas, entrada)

        etapa_preflight = self._preflight_conflictos(preset)
        etapas.append(etapa_preflight)
        if etapa_preflight.estado == "FAIL":
            return self._cerrar(contexto, etapas, entrada)

        ruta_proyecto = contexto.ruta_sandbox / preset["especificacion"]["nombre_proyecto"]
        etapa_generacion = self._ejecutar_generacion(contexto, preset, ruta_proyecto)
        etapas.append(etapa_generacion)
        if etapa_generacion.estado == "FAIL":
            etapas.append(DtoEtapaAuditoria("ETAPA 4 - Auditoría de arquitectura", "SKIP", ["No ejecutada por fallo previo"]))
            etapas.append(DtoEtapaAuditoria("ETAPA 5 - Smoke test", "SKIP", ["No ejecutada por fallo previo"]))
            return self._cerrar(contexto, etapas, entrada)

        etapas.append(self._auditar_arquitectura(ruta_proyecto))
        etapas.append(self._smoke_test(ruta_proyecto))
        return self._cerrar(contexto, etapas, entrada)

    def _preparar_contexto(self, entrada: DtoAuditoriaFinalizacionEntrada) -> _ContextoEjecucion:
        id_ejecucion = f"AUD-{datetime.now():%Y%m%d-%H%M%S}-{secrets.token_hex(2).upper()}"
        base_tmp = Path(tempfile.gettempdir())
        ruta_sandbox = entrada.resolver_ruta_sandbox(id_ejecucion=id_ejecucion, base_tmp=base_tmp)
        ruta_reporte = ruta_sandbox / "docs" / "auditoria_finalizacion_e2e.md"
        self._sistema_archivos.asegurar_directorio(str(ruta_reporte.parent))
        LOGGER.info("[%s] Sandbox de auditoría: %s", id_ejecucion, ruta_sandbox)
        return _ContextoEjecucion(id_ejecucion=id_ejecucion, ruta_sandbox=ruta_sandbox, ruta_reporte=ruta_reporte)

    def _cargar_preset(self, ruta_preset: str) -> tuple[dict[str, object] | None, DtoEtapaAuditoria]:
        try:
            datos = json.loads(Path(ruta_preset).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return None, DtoEtapaAuditoria("ETAPA 1 - Carga de preset", "FAIL", [f"No se pudo leer preset: {exc}"])

        blueprints = datos.get("blueprints")
        especificacion = datos.get("especificacion")
        if not isinstance(blueprints, list) or not blueprints or not isinstance(especificacion, dict):
            return None, DtoEtapaAuditoria(
                "ETAPA 1 - Carga de preset",
                "FAIL",
                ["Preset inválido: se requiere especificación y lista de blueprints no vacía."],
            )

        return datos, DtoEtapaAuditoria(
            "ETAPA 1 - Carga de preset",
            "PASS",
            [f"Blueprints detectados: {', '.join(str(item) for item in blueprints)}"],
        )

    def _preflight_conflictos(self, preset: dict[str, object]) -> DtoEtapaAuditoria:
        especificacion = self._construir_especificacion(preset)
        blueprints = [str(item) for item in preset["blueprints"]]
        try:
            self._crear_plan_desde_blueprints.ejecutar(especificacion, blueprints)
        except ErrorConflictoArchivos as exc:
            rutas = self._extraer_rutas_duplicadas(str(exc))
            recomendacion = (
                f"Tienes {len(rutas)} rutas duplicadas. Revisa selección de blueprints; "
                "dos generan CRUD persona."
            )
            evidencia = ["Conflicto de generación: rutas duplicadas detectadas"]
            evidencia.extend(rutas[:5])
            evidencia.append(recomendacion)
            return DtoEtapaAuditoria("ETAPA 2 - Preflight de conflictos", "FAIL", evidencia)
        except ErrorValidacion as exc:
            return DtoEtapaAuditoria("ETAPA 2 - Preflight de conflictos", "FAIL", [str(exc)])

        return DtoEtapaAuditoria("ETAPA 2 - Preflight de conflictos", "PASS", ["Sin conflictos de rutas duplicadas"])

    def _ejecutar_generacion(
        self,
        contexto: _ContextoEjecucion,
        preset: dict[str, object],
        ruta_proyecto: Path,
    ) -> DtoEtapaAuditoria:
        especificacion = self._construir_especificacion(preset)
        blueprints = [str(item) for item in preset["blueprints"]]
        entrada = GenerarProyectoMvpEntrada(
            especificacion_proyecto=especificacion,
            ruta_destino=str(contexto.ruta_sandbox),
            nombre_proyecto=especificacion.nombre_proyecto,
            blueprints=blueprints,
        )
        try:
            self._generar_proyecto_mvp.ejecutar(entrada)
        except Exception as exc:  # noqa: BLE001
            return DtoEtapaAuditoria(
                "ETAPA 3 - Ejecución en sandbox",
                "FAIL",
                [f"Fallo en generación: {exc}", traceback.format_exc()],
            )

        ruta_manifest = ruta_proyecto / "manifest.json"
        if not ruta_manifest.exists():
            return DtoEtapaAuditoria(
                "ETAPA 3 - Ejecución en sandbox",
                "FAIL",
                ["No se encontró manifest.json tras la generación."],
            )
        return DtoEtapaAuditoria(
            "ETAPA 3 - Ejecución en sandbox",
            "PASS",
            [f"Proyecto generado en {ruta_proyecto}", "manifest.json verificado"],
        )

    def _auditar_arquitectura(self, ruta_proyecto: Path) -> DtoEtapaAuditoria:
        resultado = self._auditor_arquitectura.auditar(str(ruta_proyecto))
        evidencia = list(resultado.errores) + list(resultado.warnings)
        if not evidencia:
            evidencia = ["Sin hallazgos de arquitectura"]
        estado = "PASS" if resultado.valido else "FAIL"
        return DtoEtapaAuditoria("ETAPA 4 - Auditoría de arquitectura", estado, evidencia)

    def _smoke_test(self, ruta_proyecto: Path) -> DtoEtapaAuditoria:
        evidencia: list[str] = []
        compileall = self._ejecutor_procesos.ejecutar(["python", "-m", "compileall", "."], cwd=str(ruta_proyecto))
        evidencia.append(f"compileall -> {compileall.codigo_salida}")
        if compileall.codigo_salida != 0:
            evidencia.append(compileall.stderr)
            return DtoEtapaAuditoria("ETAPA 5 - Smoke test", "FAIL", evidencia)

        hay_tests = (ruta_proyecto / "pytest.ini").exists() or (ruta_proyecto / "tests").exists()
        if not hay_tests:
            evidencia.append("No se detectaron tests en el proyecto generado")
            return DtoEtapaAuditoria("ETAPA 5 - Smoke test", "SKIP", evidencia)

        pytest_resultado = self._ejecutor_procesos.ejecutar(["pytest", "-q", "--maxfail=1"], cwd=str(ruta_proyecto))
        evidencia.append(f"pytest -> {pytest_resultado.codigo_salida}")
        if pytest_resultado.codigo_salida != 0:
            evidencia.append(pytest_resultado.stderr or pytest_resultado.stdout)
            return DtoEtapaAuditoria("ETAPA 5 - Smoke test", "FAIL", evidencia)
        return DtoEtapaAuditoria("ETAPA 5 - Smoke test", "PASS", evidencia)

    def _cerrar(
        self,
        contexto: _ContextoEjecucion,
        etapas: list[DtoEtapaAuditoria],
        entrada: DtoAuditoriaFinalizacionEntrada,
    ) -> DtoAuditoriaFinalizacionSalida:
        reporte = self._construir_reporte(contexto, etapas, entrada)
        self._sistema_archivos.escribir_texto_atomico(str(contexto.ruta_reporte), reporte)
        return DtoAuditoriaFinalizacionSalida(
            id_ejecucion=contexto.id_ejecucion,
            ruta_sandbox=str(contexto.ruta_sandbox),
            etapas=etapas,
            reporte_markdown=reporte,
            ruta_reporte=str(contexto.ruta_reporte),
        )

    def _construir_reporte(
        self,
        contexto: _ContextoEjecucion,
        etapas: list[DtoEtapaAuditoria],
        entrada: DtoAuditoriaFinalizacionEntrada,
    ) -> str:
        filas = "\n".join(f"| {etapa.nombre} | {etapa.estado} |" for etapa in etapas)
        conflictos = next((etapa for etapa in etapas if etapa.nombre.startswith("ETAPA 2") and etapa.estado == "FAIL"), None)
        bloque_conflictos = "Sin conflictos detectados."
        if conflictos is not None:
            rutas = [item for item in conflictos.evidencia if "/" in item or "." in item]
            bloque_conflictos = (
                f"- Total de rutas duplicadas: {len(rutas)}\n"
                + "\n".join(f"- {ruta}" for ruta in rutas[:5])
                + "\n- Recomendación: revisa selección de blueprints; dos generan CRUD persona."
            )

        return (
            "# Auditoría de finalización E2E\n\n"
            f"- ID ejecución: `{contexto.id_ejecucion}`\n"
            f"- Fecha/hora: `{datetime.now().isoformat(timespec='seconds')}`\n"
            f"- Ruta sandbox: `{contexto.ruta_sandbox}`\n"
            f"- Preset: `{entrada.ruta_preset}`\n\n"
            "## Etapas\n\n"
            "| Etapa | Estado |\n|---|---|\n"
            f"{filas}\n\n"
            "## Evidencias\n\n"
            + "\n".join(
                f"### {etapa.nombre}\n" + "\n".join(f"- {item}" for item in etapa.evidencia)
                for etapa in etapas
            )
            + "\n\n## Conflictos detectados\n\n"
            + bloque_conflictos
            + "\n\n## Reproducción\n\n"
            f"`python -m presentacion.cli auditar-finalizacion --preset {entrada.ruta_preset} --salida {contexto.ruta_sandbox}`\n"
            "\nLogs sugeridos: `logs/seguimiento.log` y `logs/crashes.log`.\n"
        )

    def _construir_especificacion(self, preset: dict[str, object]) -> EspecificacionProyecto:
        datos = preset["especificacion"]
        assert isinstance(datos, dict)
        clases: list[EspecificacionClase] = []
        for clase in datos.get("clases", []):
            if not isinstance(clase, dict):
                continue
            atributos = [
                EspecificacionAtributo(
                    nombre=str(atributo.get("nombre", "")),
                    tipo=str(atributo.get("tipo", "str")),
                    obligatorio=bool(atributo.get("obligatorio", False)),
                    valor_por_defecto=atributo.get("valor_por_defecto"),
                )
                for atributo in clase.get("atributos", [])
                if isinstance(atributo, dict)
            ]
            clases.append(EspecificacionClase(nombre=str(clase.get("nombre", "")), atributos=atributos))

        return EspecificacionProyecto(
            nombre_proyecto=str(datos.get("nombre_proyecto", "")),
            descripcion=str(datos.get("descripcion", "")),
            version=str(datos.get("version", "0.1.0")),
            ruta_destino=str(self._preparar_ruta_temporal()),
            clases=clases,
        )

    def _preparar_ruta_temporal(self) -> Path:
        return Path(tempfile.gettempdir())

    def _extraer_rutas_duplicadas(self, mensaje: str) -> list[str]:
        inicio = mensaje.find("[")
        fin = mensaje.rfind("]")
        if inicio == -1 or fin == -1 or fin <= inicio:
            return []
        try:
            rutas = ast.literal_eval(mensaje[inicio : fin + 1])
        except (ValueError, SyntaxError):
            return []
        if not isinstance(rutas, list):
            return []
        return [str(ruta) for ruta in rutas]

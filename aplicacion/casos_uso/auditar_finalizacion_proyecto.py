"""Caso de uso para auditar la finalización E2E de un proyecto generado."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import secrets
import tempfile
import time
import traceback

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp, GenerarProyectoMvpEntrada
from aplicacion.dtos.auditoria import (
    ConflictosFinalizacion,
    DtoAuditoriaFinalizacionEntrada,
    DtoAuditoriaFinalizacionSalida,
    ResultadoEtapa,
)
from aplicacion.errores import ErrorAplicacion, ErrorConflictoArchivos, ErrorValidacion
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos
from dominio.especificacion import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto


@dataclass(frozen=True)
class _ContextoEjecucion:
    id_ejecucion: str
    fecha_iso: str
    ruta_sandbox: Path
    ruta_evidencias: Path


class AuditarFinalizacionProyecto:
    def __init__(
        self,
        crear_plan_desde_blueprints: CrearPlanDesdeBlueprints,
        generar_proyecto_mvp: GenerarProyectoMvp,
        auditor_arquitectura: AuditarProyectoGenerado,
        ejecutor_procesos: EjecutorProcesos,
    ) -> None:
        self._crear_plan_desde_blueprints = crear_plan_desde_blueprints
        self._generar_proyecto_mvp = generar_proyecto_mvp
        self._auditor_arquitectura = auditor_arquitectura
        self._ejecutor_procesos = ejecutor_procesos

    def ejecutar(self, entrada: DtoAuditoriaFinalizacionEntrada) -> DtoAuditoriaFinalizacionSalida:
        contexto = self._preparar_contexto(entrada)
        etapas: list[ResultadoEtapa] = []
        evidencias: dict[str, str] = {
            "meta_fecha_iso": contexto.fecha_iso,
            "meta_ruta_preset": entrada.ruta_preset,
            "ruta_evidencias": str(contexto.ruta_evidencias),
            "meta_comando": (
                f"python -m presentacion.cli auditar-finalizacion --preset {entrada.ruta_preset} "
                f"--sandbox {contexto.ruta_sandbox}"
            ),
            "preparacion": f"Sandbox: {contexto.ruta_sandbox}\nEvidencias: {contexto.ruta_evidencias}",
        }
        conflictos: ConflictosFinalizacion | None = None
        etapas.append(ResultadoEtapa("Preparación", "PASS", 0, "Contexto listo"))

        preset, etapa_carga, evidencia_carga = self._medir_etapa(lambda: self._cargar_preset(entrada.ruta_preset), "Carga preset")
        etapas.append(etapa_carga)
        evidencias["carga_preset"] = evidencia_carga
        if preset is None:
            return DtoAuditoriaFinalizacionSalida(contexto.id_ejecucion, str(contexto.ruta_sandbox), etapas, None, evidencias)

        conflicto_resultado, etapa_preflight, evidencia_preflight = self._medir_etapa(
            lambda: self._preflight_conflictos(preset), "Preflight conflictos"
        )
        etapas.append(etapa_preflight)
        evidencias["preflight_conflictos"] = evidencia_preflight
        if etapa_preflight.estado == "FAIL":
            conflictos = conflicto_resultado
            motivo = "conflicto" if conflicto_resultado is not None else "fallo preflight"
            etapas.extend(
                [
                    ResultadoEtapa("Generación sandbox", "SKIP", 0, f"No ejecutada por {motivo}"),
                    ResultadoEtapa("Auditoría arquitectura", "SKIP", 0, f"No ejecutada por {motivo}"),
                    ResultadoEtapa("Smoke test", "SKIP", 0, f"No ejecutada por {motivo}"),
                ]
            )
            evidencias.setdefault("generacion_sandbox", "No ejecutada")
            evidencias.setdefault("auditoria_arquitectura", "No ejecutada")
            evidencias.setdefault("smoke_test", "No ejecutada")
            if conflicto_resultado is None:
                evidencias["incidente_id"] = contexto.id_ejecucion
            return DtoAuditoriaFinalizacionSalida(contexto.id_ejecucion, str(contexto.ruta_sandbox), etapas, conflictos, evidencias)

        ruta_proyecto = contexto.ruta_sandbox / preset["especificacion"]["nombre_proyecto"]
        _, etapa_generacion, evidencia_generacion = self._medir_etapa(
            lambda: self._generar_en_sandbox(preset, contexto.ruta_sandbox, ruta_proyecto), "Generación sandbox"
        )
        etapas.append(etapa_generacion)
        evidencias["generacion_sandbox"] = evidencia_generacion
        if etapa_generacion.estado == "FAIL":
            evidencias["incidente_id"] = contexto.id_ejecucion
            etapas.extend(
                [
                    ResultadoEtapa("Auditoría arquitectura", "SKIP", 0, "No ejecutada por fallo previo"),
                    ResultadoEtapa("Smoke test", "SKIP", 0, "No ejecutada por fallo previo"),
                ]
            )
            evidencias.setdefault("auditoria_arquitectura", "No ejecutada")
            evidencias.setdefault("smoke_test", "No ejecutada")
            return DtoAuditoriaFinalizacionSalida(contexto.id_ejecucion, str(contexto.ruta_sandbox), etapas, None, evidencias)

        _, etapa_auditoria, evidencia_auditoria = self._medir_etapa(
            lambda: self._auditar_arquitectura(ruta_proyecto), "Auditoría arquitectura"
        )
        etapas.append(etapa_auditoria)
        evidencias["auditoria_arquitectura"] = evidencia_auditoria

        _, etapa_smoke, evidencia_smoke = self._medir_etapa(lambda: self._smoke_test(ruta_proyecto), "Smoke test")
        etapas.append(etapa_smoke)
        evidencias["smoke_test"] = evidencia_smoke

        return DtoAuditoriaFinalizacionSalida(contexto.id_ejecucion, str(contexto.ruta_sandbox), etapas, None, evidencias)

    def _preparar_contexto(self, entrada: DtoAuditoriaFinalizacionEntrada) -> _ContextoEjecucion:
        id_ejecucion = f"AUD-{datetime.now():%Y%m%d-%H%M%S}-{secrets.token_hex(2).upper()}"
        ruta_sandbox = entrada.resolver_ruta_sandbox(id_ejecucion=id_ejecucion, base_tmp=Path(tempfile.gettempdir())).resolve()
        ruta_evidencias = Path("docs") / "evidencias_finalizacion" / id_ejecucion
        ruta_evidencias.mkdir(parents=True, exist_ok=True)
        ruta_sandbox.mkdir(parents=True, exist_ok=True)
        return _ContextoEjecucion(
            id_ejecucion=id_ejecucion,
            fecha_iso=datetime.now().isoformat(timespec="seconds"),
            ruta_sandbox=ruta_sandbox,
            ruta_evidencias=ruta_evidencias,
        )

    def _medir_etapa(self, accion, nombre_etapa: str):  # type: ignore[no-untyped-def]
        inicio = time.perf_counter()
        resultado, estado, resumen, evidencia = accion()
        duracion_ms = int((time.perf_counter() - inicio) * 1000)
        return resultado, ResultadoEtapa(nombre_etapa, estado, duracion_ms, resumen), evidencia

    def _cargar_preset(self, ruta_preset: str):  # type: ignore[no-untyped-def]
        try:
            datos = json.loads(Path(ruta_preset).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return None, "FAIL", "No se pudo cargar preset", str(exc)

        blueprints = datos.get("blueprints")
        especificacion = datos.get("especificacion")
        if not isinstance(blueprints, list) or not blueprints or not isinstance(especificacion, dict):
            return None, "FAIL", "Preset inválido", "Falta especificación o blueprints"
        return datos, "PASS", f"Blueprints: {len(blueprints)}", "\n".join(str(bp) for bp in blueprints)

    def _preflight_conflictos(self, preset: dict[str, object]):
        especificacion = self._construir_especificacion(preset)
        blueprints = [str(item) for item in preset["blueprints"]]
        indice: dict[str, set[str]] = {}

        for blueprint in blueprints:
            try:
                plan_parcial = self._crear_plan_desde_blueprints.ejecutar(especificacion, [blueprint])
            except (ErrorConflictoArchivos, ErrorValidacion) as exc:
                return None, "FAIL", "Error en preflight", str(exc)
            for ruta in plan_parcial.obtener_rutas():
                indice.setdefault(ruta, set()).add(blueprint)

        mapeo_conflictos = {
            ruta: sorted(list(duenios))
            for ruta, duenios in indice.items()
            if len(duenios) > 1
        }
        if mapeo_conflictos:
            rutas = sorted(mapeo_conflictos.keys())
            conflicto = ConflictosFinalizacion(
                total_rutas_duplicadas=len(rutas),
                rutas_duplicadas=rutas,
                rutas_por_blueprint=mapeo_conflictos,
            )
            top = "\n".join(f"{ruta} -> [{', '.join(mapeo_conflictos[ruta])}]" for ruta in rutas[:5])
            evidencia = (
                f"Total rutas duplicadas: {len(rutas)}\n"
                f"Primeras rutas: {', '.join(rutas[:5])}\n"
                f"Blueprints implicados:\n{top}"
            )
            return conflicto, "FAIL", "Rutas duplicadas detectadas", evidencia

        return None, "PASS", "Sin colisiones entre blueprints", "Sin rutas duplicadas"

    def _generar_en_sandbox(self, preset: dict[str, object], ruta_sandbox: Path, ruta_proyecto: Path):
        especificacion = self._construir_especificacion(preset)
        entrada = GenerarProyectoMvpEntrada(
            especificacion_proyecto=especificacion,
            ruta_destino=str(ruta_sandbox),
            nombre_proyecto=especificacion.nombre_proyecto,
            blueprints=[str(item) for item in preset["blueprints"]],
        )
        try:
            self._generar_proyecto_mvp.ejecutar(entrada)
        except (OSError, ErrorAplicacion) as exc:
            traza = traceback.format_exc()
            return None, "FAIL", "Falló generación en sandbox", f"{exc}\n{traza}"

        manifest = ruta_proyecto / "manifest.json"
        if not manifest.exists():
            return None, "FAIL", "manifest.json ausente", str(manifest)

        top_level = sorted([ruta.name for ruta in ruta_proyecto.iterdir()])
        evidencia = f"Top-level creado: {', '.join(top_level)}\nManifest: {manifest}"
        return None, "PASS", "Proyecto generado", evidencia

    def _auditar_arquitectura(self, ruta_proyecto: Path):
        resultado = self._auditor_arquitectura.auditar(str(ruta_proyecto))
        hallazgos = list(resultado.errores) + list(resultado.warnings)
        evidencia = "\n".join(hallazgos[:5]) if hallazgos else "Sin hallazgos"
        return None, ("PASS" if resultado.valido else "FAIL"), f"Hallazgos: {len(hallazgos)}", evidencia

    def _smoke_test(self, ruta_proyecto: Path):
        compileall = self._ejecutor_procesos.ejecutar(["python", "-m", "compileall", "."], cwd=str(ruta_proyecto))
        evidencia = [
            f"compileall exit={compileall.codigo_salida}",
            (compileall.stdout or compileall.stderr)[:1000],
        ]
        if compileall.codigo_salida != 0:
            return None, "FAIL", "compileall falló", "\n".join(evidencia)

        hay_tests = (ruta_proyecto / "pytest.ini").exists() or (ruta_proyecto / "tests").exists()
        if not hay_tests:
            evidencia.append("pytest SKIP (sin tests)")
            return None, "SKIP", "Sin tests generados", "\n".join(evidencia)

        pytest_res = self._ejecutor_procesos.ejecutar(["pytest", "-q", "--maxfail=1"], cwd=str(ruta_proyecto))
        evidencia.extend([f"pytest exit={pytest_res.codigo_salida}", (pytest_res.stdout or pytest_res.stderr)[:1000]])
        if pytest_res.codigo_salida != 0:
            return None, "FAIL", "pytest falló", "\n".join(evidencia)
        return None, "PASS", "compileall y pytest OK", "\n".join(evidencia)

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
            ruta_destino=str(Path(tempfile.gettempdir())),
            clases=clases,
        )

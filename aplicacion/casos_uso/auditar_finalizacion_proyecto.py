"""Caso de uso para auditar la finalización E2E de un proyecto generado."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import json
import logging
from pathlib import Path
import secrets
import shutil
import tempfile
import time
import traceback
from types import TracebackType

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp, GenerarProyectoMvpEntrada
from aplicacion.casos_uso.validar_compatibilidad_blueprints import ValidarCompatibilidadBlueprints
from aplicacion.dtos.auditoria import (
    CONFLICTO,
    INESPERADO,
    IO,
    VALIDACION,
    DtoAuditoriaFinalizacionEntrada,
    DtoConflictosRutasInforme,
    DtoErrorTecnicoInforme,
    DtoEtapaInforme,
    EvidenciasCompat,
    DtoInformeFinalizacion,
)
from aplicacion.errores import ErrorConflictoArchivos
from dominio.especificacion import ErrorValidacionDominio
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos
from aplicacion.puertos.planificador_blueprint_puerto import PlanificadorBlueprintPuerto
from dominio.especificacion import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto

LOGGER = logging.getLogger(__name__)


class AuditarFinalizacionProyecto:
    def __init__(
        self,
        planificador_blueprints: PlanificadorBlueprintPuerto | None = None,
        generar_proyecto_mvp: GenerarProyectoMvp | None = None,
        auditor_arquitectura: AuditarProyectoGenerado | None = None,
        ejecutor_procesos: EjecutorProcesos | None = None,
        validador_compatibilidad_blueprints: ValidarCompatibilidadBlueprints | None = None,
        **kwargs: object,
    ) -> None:
        planificador = planificador_blueprints or kwargs.get("crear_plan_desde_blueprints")
        generador = generar_proyecto_mvp or kwargs.get("generar_proyecto_mvp")
        auditor = auditor_arquitectura or kwargs.get("auditor_arquitectura")
        ejecutor = ejecutor_procesos or kwargs.get("ejecutor_procesos")
        if planificador is None or generador is None or auditor is None or ejecutor is None:
            raise ValueError("Se requiere planificador_blueprints")
        self._planificador = planificador
        self._generador = generador
        self._auditor_arquitectura = auditor
        self._ejecutor = ejecutor
        self._validador_compatibilidad = validador_compatibilidad_blueprints or ValidarCompatibilidadBlueprints()

    def ejecutar(self, entrada: DtoAuditoriaFinalizacionEntrada | None = None, **kwargs: object) -> DtoInformeFinalizacion:
        if isinstance(entrada, DtoAuditoriaFinalizacionEntrada):
            ruta_preset = entrada.ruta_preset
            ruta_sandbox = entrada.ruta_salida_auditoria or str(Path(tempfile.gettempdir()) / "auditoria")
            ruta_evidencias = kwargs.get("ruta_evidencias", "docs/evidencias_finalizacion")
            ejecutar_smoke_test = bool(kwargs.get("ejecutar_smoke_test", True))
            ejecutar_auditoria_arquitectura = bool(kwargs.get("ejecutar_auditoria_arquitectura", True))
        else:
            ruta_preset = str(kwargs["ruta_preset"])
            ruta_sandbox = str(kwargs["ruta_sandbox"])
            ruta_evidencias = str(kwargs["ruta_evidencias"])
            ejecutar_smoke_test = bool(kwargs.get("ejecutar_smoke_test", False))
            ejecutar_auditoria_arquitectura = bool(kwargs.get("ejecutar_auditoria_arquitectura", False))

        id_ejecucion = f"AUD-{datetime.now():%Y%m%d-%H%M%S}-{secrets.token_hex(2).upper()}"
        fecha_iso = datetime.now().isoformat(timespec="seconds")
        sandbox = Path(ruta_sandbox)
        evidencias_dir = Path(ruta_evidencias) / id_ejecucion

        etapas: list[DtoEtapaInforme] = []
        warnings: list[str] = []
        conflictos = DtoConflictosRutasInforme()
        conflictos_declarativos = []
        error_tecnico: DtoErrorTecnicoInforme | None = None

        def medir(nombre: str, fn):
            inicio = time.perf_counter()
            try:
                return fn(), "PASS", "ok", None
            except Exception as exc:  # noqa: BLE001
                return None, "FAIL", str(exc), exc
            finally:
                dur = max(1, int((time.perf_counter() - inicio) * 1000))
                nonlocal ultima_duracion
                ultima_duracion = dur

        ultima_duracion = 1
        estado_global = "PASS"
        tipo_fallo = "N/A"
        codigo_fallo = "N/A"

        # A preparación
        def _prep():
            if sandbox.exists():
                shutil.rmtree(sandbox)
            sandbox.mkdir(parents=True, exist_ok=True)
            evidencias_dir.mkdir(parents=True, exist_ok=True)

        _, estado, resumen, exc = medir("Preparación", _prep)
        etapas.append(DtoEtapaInforme("Preparación", estado, ultima_duracion, resumen, [f"sandbox={sandbox}", f"evidencias={evidencias_dir}"]))
        if exc:
            estado_global, tipo_fallo, codigo_fallo = "FAIL", IO, "IO-001"
            error_tecnico = self._error(exc)
            return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico, conflictos_declarativos)

        # B carga
        def _cargar():
            return json.loads(Path(ruta_preset).read_text(encoding="utf-8"))

        preset, estado, resumen, exc = medir("Carga preset", _cargar)
        etapas.append(DtoEtapaInforme("Carga preset", estado, ultima_duracion, resumen, [ruta_preset], tipo_fallo=IO if exc else None))
        if exc:
            estado_global, tipo_fallo, codigo_fallo = "FAIL", IO, "IO-001"
            error_tecnico = self._error(exc)
            return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico, conflictos_declarativos)

        assert isinstance(preset, dict)
        especificacion = self._construir_especificacion(preset)
        blueprints = [str(bp) for bp in preset.get("blueprints", [])]

        # C validación
        def _validar():
            if not blueprints:
                raise ValueError("Preset sin blueprints")
            resultado = self._validador_compatibilidad.ejecutar(blueprints, hay_clases=bool(especificacion.clases))
            if (not especificacion.clases and "crud_json" in blueprints) or any(conflicto.codigo == "VAL-DECL-001" for conflicto in resultado.conflictos):
                raise ValueError("Al menos 1 clase requerida")

        _, estado, resumen, exc = medir("Preflight validación entrada", _validar)
        etapas.append(DtoEtapaInforme("Preflight validación entrada", estado, ultima_duracion, resumen, [f"blueprints={blueprints}", "Warnings declarativos: crud_json y crud_sqlite: elige 1 CRUD"] if exc and "Al menos 1 clase" in resumen and {"crud_json", "crud_sqlite"}.intersection(set(blueprints)) else [f"blueprints={blueprints}"], tipo_fallo=VALIDACION if exc else None, codigo="VAL-001" if exc else None, mensaje_usuario="crud_json requiere al menos una clase" if exc else None))
        if exc:
            estado_global, tipo_fallo, codigo_fallo = "FAIL", VALIDACION, "VAL-001"
            error_tecnico = self._error(exc)
            etapas.extend([
                DtoEtapaInforme("Preflight conflictos de rutas", "SKIP", 0, "No ejecutada por validación", []),
                DtoEtapaInforme("Generación sandbox", "SKIP", 0, "No ejecutada por validación", []),
                DtoEtapaInforme("Auditoría arquitectura", "SKIP", 0, "No ejecutada por validación", []),
                DtoEtapaInforme("Smoke test", "SKIP", 0, "No ejecutada por validación", []),
            ])
            return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico, conflictos_declarativos)

        # D compatibilidad declarativa
        def _compatibilidad_declarativa():
            return self._validador_compatibilidad.ejecutar(blueprints, hay_clases=bool(especificacion.clases))

        resultado_compatibilidad, estado, resumen, exc = medir("Preflight compatibilidad declarativa", _compatibilidad_declarativa)
        if resultado_compatibilidad and not resultado_compatibilidad.es_valido:
            estado = "FAIL"
            resumen = f"{len(resultado_compatibilidad.conflictos)} conflictos declarativos"
            warnings.extend(resultado_compatibilidad.warnings)
            conflictos_declarativos = resultado_compatibilidad.conflictos
        etapas.append(
            DtoEtapaInforme(
                "Preflight compatibilidad declarativa",
                estado,
                ultima_duracion,
                resumen,
                [
                    f"{conflicto.codigo}: {conflicto.blueprint_a} / {conflicto.blueprint_b or 'N/A'} - {conflicto.motivo}"
                    for conflicto in (resultado_compatibilidad.conflictos if resultado_compatibilidad else [])
                ],
            )
        )
        if exc or (resultado_compatibilidad and not resultado_compatibilidad.es_valido):
            estado_global, tipo_fallo, codigo_fallo = "FAIL", CONFLICTO, "CON-DECL-001"
            if resultado_compatibilidad and resultado_compatibilidad.conflictos:
                codigo_fallo = resultado_compatibilidad.conflictos[0].codigo
            if exc:
                error_tecnico = self._error(exc)
            etapas.extend([
                DtoEtapaInforme("Preflight conflictos de rutas", "SKIP", 0, "No ejecutada por conflicto declarativo", []),
                DtoEtapaInforme("Generación sandbox", "SKIP", 0, "No ejecutada por conflicto declarativo", []),
                DtoEtapaInforme("Auditoría arquitectura", "SKIP", 0, "No ejecutada por conflicto declarativo", []),
                DtoEtapaInforme("Smoke test", "SKIP", 0, "No ejecutada por conflicto declarativo", []),
            ])
            return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico, conflictos_declarativos)

        # E conflictos
        def _conflictos():
            indice: dict[str, list[str]] = {}
            for blueprint in blueprints:
                if hasattr(self._planificador, "obtener_rutas_generadas"):
                    rutas = self._planificador.obtener_rutas_generadas(blueprint, especificacion)
                else:
                    plan = self._planificador.ejecutar(especificacion, [blueprint])
                    rutas = [archivo.ruta_relativa for archivo in getattr(plan, "archivos", [])]
                for ruta in rutas:
                    indice.setdefault(ruta, []).append(blueprint)
            return {ruta: sorted(set(duenos)) for ruta, duenos in indice.items() if len(set(duenos)) > 1}

        mapeo, estado, resumen, exc = medir("Preflight conflictos de rutas", _conflictos)
        mapeo = mapeo or {}
        if mapeo:
            estado = "FAIL"
            resumen = f"{len(mapeo)} rutas duplicadas"
        ejemplos = [f"{ruta} -> [{', '.join(duenos)}]" for ruta, duenos in list(sorted(mapeo.items()))[:10]]
        etapas.append(DtoEtapaInforme("Preflight conflictos de rutas", estado, ultima_duracion, resumen, ejemplos, tipo_fallo=CONFLICTO if (exc or mapeo) else None, codigo="CON-001" if (exc or mapeo) else None))
        if exc or mapeo:
            estado_global, tipo_fallo, codigo_fallo = "FAIL", CONFLICTO, "CON-001"
            if exc:
                error_tecnico = self._error(exc)
            conflictos = DtoConflictosRutasInforme(total=len(mapeo), ejemplos_top=ejemplos, rutas_por_blueprint=mapeo)
            etapas.extend([
                DtoEtapaInforme("Generación sandbox", "SKIP", 0, "No ejecutada por conflicto", []),
                DtoEtapaInforme("Auditoría arquitectura", "SKIP", 0, "No ejecutada por conflicto", []),
                DtoEtapaInforme("Smoke test", "SKIP", 0, "No ejecutada por conflicto", []),
            ])
            return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico, conflictos_declarativos)

        # F generación
        ruta_proyecto = sandbox / especificacion.nombre_proyecto
        def _generar():
            self._generador.ejecutar(
                GenerarProyectoMvpEntrada(
                    especificacion_proyecto=especificacion,
                    ruta_destino=str(sandbox),
                    nombre_proyecto=especificacion.nombre_proyecto,
                    blueprints=blueprints,
                )
            )

        _, estado, resumen, exc = medir("Generación sandbox", _generar)
        etapas.append(DtoEtapaInforme("Generación sandbox", estado, ultima_duracion, resumen, [str(ruta_proyecto)]))
        if exc:
            estado_global, tipo_fallo, codigo_fallo = "FAIL", IO, "IO-001"
            error_tecnico = self._error(exc)
            etapas.extend([
                DtoEtapaInforme("Auditoría arquitectura", "SKIP", 0, "No ejecutada por fallo previo", []),
                DtoEtapaInforme("Smoke test", "SKIP", 0, "No ejecutada por fallo previo", []),
            ])
            return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico, conflictos_declarativos)

        # G
        if ejecutar_auditoria_arquitectura:
            _, estado, resumen, exc = medir("Auditoría arquitectura", lambda: self._auditor_arquitectura.auditar(str(ruta_proyecto)))
            etapas.append(DtoEtapaInforme("Auditoría arquitectura", estado if not exc else "FAIL", ultima_duracion, resumen, []))
        else:
            etapas.append(DtoEtapaInforme("Auditoría arquitectura", "SKIP", 0, "Desactivada", []))

        # H
        if ejecutar_smoke_test:
            _, estado, resumen, exc = medir("Smoke test", lambda: self._smoke(ruta_proyecto))
            etapas.append(DtoEtapaInforme("Smoke test", "PASS" if not exc else "FAIL", ultima_duracion, resumen, [], tipo_fallo=IO if exc else None))
        else:
            etapas.append(DtoEtapaInforme("Smoke test", "SKIP", 0, "Desactivado", []))

        return self._finalizar(
            id_ejecucion,
            fecha_iso,
            ruta_preset,
            sandbox,
            evidencias_dir,
            estado_global,
            tipo_fallo,
            codigo_fallo,
            etapas,
            conflictos,
            warnings,
            error_tecnico,
            conflictos_declarativos,
        )

    def _smoke(self, ruta_proyecto: Path) -> None:
        resultado_compile = self._ejecutor.ejecutar(["python", "-m", "compileall", "."], cwd=str(ruta_proyecto))
        if getattr(resultado_compile, "codigo_salida", 0) != 0:
            raise OSError("Smoke compileall falló")
        if (ruta_proyecto / "tests").exists():
            resultado_pytest = self._ejecutor.ejecutar(["pytest", "-q"], cwd=str(ruta_proyecto))
            if getattr(resultado_pytest, "codigo_salida", 0) != 0:
                raise OSError("Smoke pytest falló")

    def _finalizar(
        self,
        id_ejecucion: str,
        fecha_iso: str,
        ruta_preset: str,
        sandbox: Path,
        evidencias_dir: Path,
        estado_global: str,
        tipo_fallo: str,
        codigo_fallo: str,
        etapas: list[DtoEtapaInforme],
        conflictos: DtoConflictosRutasInforme,
        warnings: list[str],
        error_tecnico: DtoErrorTecnicoInforme | None,
        conflictos_declarativos: list | None = None,
    ) -> DtoInformeFinalizacion:
        informe = DtoInformeFinalizacion(
            id_ejecucion=id_ejecucion,
            fecha_iso=fecha_iso,
            preset_origen=ruta_preset,
            sandbox=str(sandbox),
            evidencias=EvidenciasCompat(str(evidencias_dir), self._mapa_evidencias(etapas, str(evidencias_dir), ruta_preset)),
            estado_global=estado_global,
            tipo_fallo_dominante=tipo_fallo,
            codigo_fallo=codigo_fallo,
            etapas=etapas,
            conflictos_rutas=conflictos,
            conflictos_declarativos=conflictos_declarativos or [],
            warnings=warnings,
            error_tecnico=error_tecnico,
        )
        self._guardar_evidencias(informe, evidencias_dir, Path(ruta_preset))
        LOGGER.info("Auditoría finalización id=%s estado=%s", id_ejecucion, estado_global)
        return informe

    def _guardar_evidencias(self, informe: DtoInformeFinalizacion, evidencias_dir: Path, ruta_preset: Path) -> None:
        evidencias_dir.mkdir(parents=True, exist_ok=True)
        (evidencias_dir / "informe.json").write_text(json.dumps(asdict(informe), ensure_ascii=False, indent=2), encoding="utf-8")
        from aplicacion.servicios.generador_informe_finalizacion_md import generar_markdown

        (evidencias_dir / "informe.md").write_text(generar_markdown(informe), encoding="utf-8")
        if ruta_preset.exists():
            shutil.copy2(ruta_preset, evidencias_dir / ruta_preset.name)

    def _mapa_evidencias(self, etapas: list[DtoEtapaInforme], ruta_evidencias: str, ruta_preset: str) -> dict[str, str]:
        evidencias = {
            "ruta_evidencias": ruta_evidencias,
            "meta_ruta_preset": ruta_preset,
        }
        for etapa in etapas:
            clave = etapa.nombre.lower().replace(" ", "_").replace("ó", "o")
            clave = clave.replace("_de_", "_")
            contenido = "\n".join(etapa.evidencias_texto) if etapa.evidencias_texto else etapa.resumen
            if clave == "preflight_conflictos_rutas" and etapa.estado == "FAIL":
                contenido = f"total rutas duplicadas: {len(etapa.evidencias_texto)}\n" + contenido
            evidencias[clave] = contenido
        return evidencias

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

    def _error(self, exc: Exception) -> DtoErrorTecnicoInforme:
        origen = self._origen(exc.__traceback__)
        linea_raise = self._linea_raise(exc.__traceback__)
        stack = traceback.format_exception(type(exc), exc, exc.__traceback__)
        lineas = "".join(stack).splitlines()[-40:]
        return DtoErrorTecnicoInforme(
            tipo=type(exc).__name__,
            mensaje=str(exc),
            origen=origen,
            linea_raise=linea_raise,
            stacktrace_recortado=lineas,
        )

    def _origen(self, traza: TracebackType | None) -> str:
        if traza is None:
            return "N/D"
        resumen = traceback.extract_tb(traza)
        if not resumen:
            return "N/D"
        final = resumen[-1]
        return f"{Path(final.filename).name}:{final.name}:{final.lineno}"

    def _linea_raise(self, traza: TracebackType | None) -> str:
        if traza is None:
            return "N/D"
        resumen = traceback.extract_tb(traza)
        if not resumen:
            return "N/D"
        final = resumen[-1]
        return f"{Path(final.filename).name}:{final.lineno}"

    def _clasificar_fallo(self, exc: Exception) -> str:
        if isinstance(exc, (ErrorValidacionDominio, ValueError, TypeError)):
            return VALIDACION
        if isinstance(exc, ErrorConflictoArchivos):
            return CONFLICTO
        if isinstance(exc, OSError):
            return IO
        return INESPERADO

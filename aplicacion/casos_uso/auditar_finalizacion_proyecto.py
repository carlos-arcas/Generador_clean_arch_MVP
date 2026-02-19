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
from aplicacion.dtos.auditoria import (
    CONFLICTO,
    INESPERADO,
    IO,
    VALIDACION,
    DtoAuditoriaFinalizacionEntrada,
    DtoConflictosRutasInforme,
    DtoErrorTecnicoInforme,
    DtoEtapaInforme,
    DtoInformeFinalizacion,
)
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos
from aplicacion.puertos.planificador_blueprint_puerto import PlanificadorBlueprintPuerto
from dominio.especificacion import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto

LOGGER = logging.getLogger(__name__)


class AuditarFinalizacionProyecto:
    def __init__(
        self,
        planificador_blueprints: PlanificadorBlueprintPuerto,
        generar_proyecto_mvp: GenerarProyectoMvp,
        auditor_arquitectura: AuditarProyectoGenerado,
        ejecutor_procesos: EjecutorProcesos,
    ) -> None:
        self._planificador = planificador_blueprints
        self._generador = generar_proyecto_mvp
        self._auditor_arquitectura = auditor_arquitectura
        self._ejecutor = ejecutor_procesos

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
            return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico)

        # B carga
        def _cargar():
            return json.loads(Path(ruta_preset).read_text(encoding="utf-8"))

        preset, estado, resumen, exc = medir("Carga preset", _cargar)
        etapas.append(DtoEtapaInforme("Carga preset", estado, ultima_duracion, resumen, [ruta_preset]))
        if exc:
            estado_global, tipo_fallo, codigo_fallo = "FAIL", IO, "IO-001"
            error_tecnico = self._error(exc)
            return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico)

        assert isinstance(preset, dict)
        especificacion = self._construir_especificacion(preset)
        blueprints = [str(bp) for bp in preset.get("blueprints", [])]

        # C validación
        def _validar():
            if not blueprints:
                raise ValueError("Preset sin blueprints")
            if not especificacion.clases:
                raise ValueError("Al menos 1 clase requerida")

        _, estado, resumen, exc = medir("Preflight validación entrada", _validar)
        etapas.append(DtoEtapaInforme("Preflight validación entrada", estado, ultima_duracion, resumen, [f"blueprints={blueprints}"]))
        if exc:
            estado_global, tipo_fallo, codigo_fallo = "FAIL", VALIDACION, "VAL-001"
            error_tecnico = self._error(exc)
            etapas.extend([
                DtoEtapaInforme("Preflight conflictos de rutas", "SKIP", 0, "No ejecutada por validación", []),
                DtoEtapaInforme("Generación sandbox", "SKIP", 0, "No ejecutada por validación", []),
                DtoEtapaInforme("Auditoría arquitectura", "SKIP", 0, "No ejecutada por validación", []),
                DtoEtapaInforme("Smoke test", "SKIP", 0, "No ejecutada por validación", []),
            ])
            return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico)

        # D conflictos
        def _conflictos():
            indice: dict[str, list[str]] = {}
            for blueprint in blueprints:
                rutas = self._planificador.obtener_rutas_generadas(blueprint, especificacion)
                for ruta in rutas:
                    indice.setdefault(ruta, []).append(blueprint)
            return {ruta: sorted(set(duenos)) for ruta, duenos in indice.items() if len(set(duenos)) > 1}

        mapeo, estado, resumen, exc = medir("Preflight conflictos de rutas", _conflictos)
        mapeo = mapeo or {}
        if mapeo:
            estado = "FAIL"
            resumen = f"{len(mapeo)} rutas duplicadas"
        ejemplos = [f"{ruta} -> [{', '.join(duenos)}]" for ruta, duenos in list(sorted(mapeo.items()))[:10]]
        etapas.append(DtoEtapaInforme("Preflight conflictos de rutas", estado, ultima_duracion, resumen, ejemplos))
        if exc or mapeo:
            estado_global, tipo_fallo, codigo_fallo = "FAIL", CONFLICTO, "CON-001"
            if exc:
                error_tecnico = self._error(exc)
            conflictos = DtoConflictosRutasInforme(total=len(mapeo), ejemplos_top=ejemplos)
            etapas.extend([
                DtoEtapaInforme("Generación sandbox", "SKIP", 0, "No ejecutada por conflicto", []),
                DtoEtapaInforme("Auditoría arquitectura", "SKIP", 0, "No ejecutada por conflicto", []),
                DtoEtapaInforme("Smoke test", "SKIP", 0, "No ejecutada por conflicto", []),
            ])
            return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico)

        # E generación
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
            return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico)

        # F
        if ejecutar_auditoria_arquitectura:
            _, estado, resumen, exc = medir("Auditoría arquitectura", lambda: self._auditor_arquitectura.auditar(str(ruta_proyecto)))
            etapas.append(DtoEtapaInforme("Auditoría arquitectura", estado if not exc else "FAIL", ultima_duracion, resumen, []))
        else:
            etapas.append(DtoEtapaInforme("Auditoría arquitectura", "SKIP", 0, "Desactivada", []))

        # G
        if ejecutar_smoke_test:
            _, estado, resumen, exc = medir("Smoke test", lambda: self._smoke(ruta_proyecto))
            etapas.append(DtoEtapaInforme("Smoke test", "PASS" if not exc else "FAIL", ultima_duracion, resumen, []))
        else:
            etapas.append(DtoEtapaInforme("Smoke test", "SKIP", 0, "Desactivado", []))

        return self._finalizar(id_ejecucion, fecha_iso, ruta_preset, sandbox, evidencias_dir, estado_global, tipo_fallo, codigo_fallo, etapas, conflictos, warnings, error_tecnico)

    def _smoke(self, ruta_proyecto: Path) -> None:
        self._ejecutor.ejecutar(["python", "-m", "compileall", "."], cwd=str(ruta_proyecto))
        if (ruta_proyecto / "tests").exists():
            self._ejecutor.ejecutar(["pytest", "-q"], cwd=str(ruta_proyecto))

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
    ) -> DtoInformeFinalizacion:
        informe = DtoInformeFinalizacion(
            id_ejecucion=id_ejecucion,
            fecha_iso=fecha_iso,
            preset_origen=ruta_preset,
            sandbox=str(sandbox),
            evidencias=str(evidencias_dir),
            estado_global=estado_global,
            tipo_fallo_dominante=tipo_fallo,
            codigo_fallo=codigo_fallo,
            etapas=etapas,
            conflictos_rutas=conflictos,
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
        shutil.copy2(ruta_preset, evidencias_dir / ruta_preset.name)

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

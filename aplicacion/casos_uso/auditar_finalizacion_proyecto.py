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
from types import TracebackType

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp, GenerarProyectoMvpEntrada
from aplicacion.dtos.auditoria import (
    CONFLICTO,
    INESPERADO,
    IO,
    VALIDACION,
    ConflictosFinalizacion,
    DtoAuditoriaFinalizacionEntrada,
    DtoAuditoriaFinalizacionSalida,
    ResultadoEtapa,
)
from aplicacion.errores import ErrorAplicacion, ErrorConflictoArchivos, ErrorValidacion
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos
from dominio.errores import ErrorValidacionDominio
from dominio.especificacion import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto


@dataclass(frozen=True)
class _ContextoEjecucion:
    id_ejecucion: str
    fecha_iso: str
    ruta_sandbox: Path
    ruta_evidencias: Path


@dataclass(frozen=True)
class _ReglaBlueprint:
    blueprint: str
    regla: str
    accion: str


@dataclass(frozen=True)
class _FalloEtapa:
    tipo_fallo: str
    codigo: str
    mensaje_usuario: str
    detalle_tecnico: str


class AuditarFinalizacionProyecto:
    _REGLAS_BLUEPRINTS: tuple[_ReglaBlueprint, ...] = (
        _ReglaBlueprint(
            blueprint="crud_json",
            regla="requiere al menos 1 clase",
            accion="añade al menos una clase en la especificación o elimina crud_json del preset",
        ),
        _ReglaBlueprint(
            blueprint="crud_json",
            regla="requiere entidad 'persona'",
            accion="añade la clase Persona en la especificación o elimina crud_json del preset",
        ),
    )
    _INCOMPATIBILIDADES_DECLARATIVAS: tuple[tuple[str, str, str], ...] = (
        (
            "crud_json",
            "crud_sqlite",
            "Incompatibilidad declarativa detectada: crud_json y crud_sqlite generan CRUD para la misma entidad. "
            "Recomendación: elige 1 CRUD.",
        ),
    )

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
        etapas: list[ResultadoEtapa] = []
        contexto, etapa_preparacion, evidencia_preparacion = self._medir_etapa(
            lambda: self._preparar_contexto(entrada), "Preparación"
        )
        assert contexto is not None
        etapas.append(etapa_preparacion)
        evidencias: dict[str, str] = {
            "meta_fecha_iso": contexto.fecha_iso,
            "meta_ruta_preset": entrada.ruta_preset,
            "ruta_evidencias": str(contexto.ruta_evidencias),
            "meta_comando": (
                f"python -m presentacion.cli auditar-finalizacion --preset {entrada.ruta_preset} "
                f"--sandbox {contexto.ruta_sandbox}"
            ),
            "preparacion": evidencia_preparacion,
        }
        conflictos: ConflictosFinalizacion | None = None

        preset, etapa_carga, evidencia_carga = self._medir_etapa(lambda: self._cargar_preset(entrada.ruta_preset), "Carga preset")
        etapas.append(etapa_carga)
        evidencias["carga_preset"] = evidencia_carga
        if preset is None:
            self._registrar_incidente_si_aplica(etapa_carga, evidencias, contexto.id_ejecucion)
            return DtoAuditoriaFinalizacionSalida(contexto.id_ejecucion, str(contexto.ruta_sandbox), etapas, None, evidencias)

        _, etapa_validacion, evidencia_validacion = self._medir_etapa(
            lambda: self._preflight_validacion_entrada(preset), "Preflight validación entrada"
        )
        etapas.append(etapa_validacion)
        evidencias["preflight_validacion_entrada"] = evidencia_validacion
        if etapa_validacion.estado == "FAIL":
            etapas.append(ResultadoEtapa("Preflight conflictos de rutas", "SKIP", 0, "No ejecutada por fallo de validación"))
            evidencias.setdefault("preflight_conflictos_rutas", "No ejecutada")
            self._anexar_etapas_skip(etapas, "fallo de validación")
            self._completar_evidencias_skip(evidencias)
            self._registrar_incidente_si_aplica(etapa_validacion, evidencias, contexto.id_ejecucion)
            return DtoAuditoriaFinalizacionSalida(contexto.id_ejecucion, str(contexto.ruta_sandbox), etapas, None, evidencias)

        conflicto_resultado, etapa_conflictos, evidencia_conflictos = self._medir_etapa(
            lambda: self._preflight_conflictos_rutas(preset), "Preflight conflictos de rutas"
        )
        etapas.append(etapa_conflictos)
        evidencias["preflight_conflictos_rutas"] = evidencia_conflictos
        if etapa_conflictos.estado == "FAIL":
            conflictos = conflicto_resultado
            self._anexar_etapas_skip(etapas, "conflicto de rutas")
            self._completar_evidencias_skip(evidencias)
            self._registrar_incidente_si_aplica(etapa_conflictos, evidencias, contexto.id_ejecucion)
            return DtoAuditoriaFinalizacionSalida(contexto.id_ejecucion, str(contexto.ruta_sandbox), etapas, conflictos, evidencias)

        ruta_proyecto = contexto.ruta_sandbox / str(preset["especificacion"]["nombre_proyecto"])
        _, etapa_generacion, evidencia_generacion = self._medir_etapa(
            lambda: self._generar_en_sandbox(preset, contexto.ruta_sandbox, ruta_proyecto), "Generación sandbox"
        )
        etapas.append(etapa_generacion)
        evidencias["generacion_sandbox"] = evidencia_generacion
        if etapa_generacion.estado == "FAIL":
            self._registrar_incidente_si_aplica(etapa_generacion, evidencias, contexto.id_ejecucion)
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

    def _preparar_contexto(self, entrada: DtoAuditoriaFinalizacionEntrada):
        id_ejecucion = f"AUD-{datetime.now():%Y%m%d-%H%M%S}-{secrets.token_hex(2).upper()}"
        ruta_sandbox = entrada.resolver_ruta_sandbox(id_ejecucion=id_ejecucion, base_tmp=Path(tempfile.gettempdir())).resolve()
        ruta_evidencias = Path("docs") / "evidencias_finalizacion" / id_ejecucion
        ruta_evidencias.mkdir(parents=True, exist_ok=True)
        ruta_sandbox.mkdir(parents=True, exist_ok=True)
        contexto = _ContextoEjecucion(
            id_ejecucion=id_ejecucion,
            fecha_iso=datetime.now().isoformat(timespec="seconds"),
            ruta_sandbox=ruta_sandbox,
            ruta_evidencias=ruta_evidencias,
        )
        evidencia = f"Sandbox: {contexto.ruta_sandbox}\nEvidencias: {contexto.ruta_evidencias}"
        return contexto, "PASS", "Contexto listo", evidencia, None

    def _medir_etapa(self, accion, nombre_etapa: str):  # type: ignore[no-untyped-def]
        inicio = time.perf_counter()
        resultado, estado, resumen, evidencia, fallo = accion()
        duracion_ms = int((time.perf_counter() - inicio) * 1000)
        if estado in {"PASS", "FAIL"} and duracion_ms == 0:
            duracion_ms = 1
        etapa = ResultadoEtapa(
            nombre=nombre_etapa,
            estado=estado,
            duracion_ms=duracion_ms,
            resumen=resumen,
            tipo_fallo=fallo.tipo_fallo if fallo else None,
            codigo=fallo.codigo if fallo else None,
            mensaje_usuario=fallo.mensaje_usuario if fallo else None,
            detalle_tecnico=fallo.detalle_tecnico if fallo else None,
        )
        return resultado, etapa, evidencia

    def _cargar_preset(self, ruta_preset: str):  # type: ignore[no-untyped-def]
        try:
            datos = json.loads(Path(ruta_preset).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fallo = self._crear_fallo(exc=exc, codigo="IO-001", mensaje_usuario="No se pudo cargar el preset", tipo_forzado=IO)
            return None, "FAIL", "No se pudo cargar preset", fallo.detalle_tecnico, fallo

        blueprints = datos.get("blueprints")
        especificacion = datos.get("especificacion")
        if not isinstance(blueprints, list) or not blueprints or not isinstance(especificacion, dict):
            exc = ErrorValidacion("Falta especificación o blueprints")
            fallo = self._crear_fallo(
                exc=exc,
                codigo="VAL-000",
                mensaje_usuario="El preset debe incluir especificación y al menos un blueprint",
                tipo_forzado=VALIDACION,
            )
            return None, "FAIL", "Preset inválido", fallo.detalle_tecnico, fallo
        return datos, "PASS", f"Blueprints: {len(blueprints)}", "\n".join(str(bp) for bp in blueprints), None

    def _preflight_validacion_entrada(self, preset: dict[str, object]):
        especificacion = self._construir_especificacion(preset)
        blueprints = [str(item) for item in preset["blueprints"]]
        clases = list(especificacion.clases)
        warnings = self._warnings_incompatibilidades(blueprints)
        prefijo_warnings = self._serializar_warnings(warnings)

        for regla in self._REGLAS_BLUEPRINTS:
            if regla.blueprint not in blueprints:
                continue
            if regla.regla == "requiere al menos 1 clase" and not clases:
                mensaje = (
                    "crud_json requiere al menos una clase. "
                    "Blueprint culpable: crud_json. Regla: requiere al menos 1 clase. "
                    "Acción: añade al menos una clase en la especificación o elimina crud_json del preset"
                )
                exc = ErrorValidacionDominio("El blueprint crud_json requiere al menos una clase en la especificación.")
                fallo = self._crear_fallo(exc=exc, codigo="VAL-001", mensaje_usuario=mensaje, tipo_forzado=VALIDACION)
                evidencia = f"{prefijo_warnings}\n\n{fallo.detalle_tecnico}" if prefijo_warnings else fallo.detalle_tecnico
                return None, "FAIL", "Validación de blueprint fallida", evidencia, fallo
            if regla.regla == "requiere entidad 'persona'" and clases and not self._existe_clase_persona(clases):
                mensaje = (
                    "crud_json requiere entidad persona. Blueprint culpable: crud_json. "
                    "Regla: requiere entidad 'persona'. Acción: añade la clase Persona en la especificación "
                    "o elimina crud_json del preset"
                )
                exc = ErrorValidacionDominio("El blueprint crud_json requiere entidad Persona.")
                fallo = self._crear_fallo(exc=exc, codigo="VAL-002", mensaje_usuario=mensaje, tipo_forzado=VALIDACION)
                evidencia = f"{prefijo_warnings}\n\n{fallo.detalle_tecnico}" if prefijo_warnings else fallo.detalle_tecnico
                return None, "FAIL", "Validación de blueprint fallida", evidencia, fallo

        evidencia = prefijo_warnings or "Reglas de blueprint satisfechas"
        return None, "PASS", "Validación de entrada OK", evidencia, None

    def _preflight_conflictos_rutas(self, preset: dict[str, object]):
        especificacion = self._construir_especificacion(preset)
        blueprints = [str(item) for item in preset["blueprints"]]
        indice: dict[str, set[str]] = {}

        for blueprint in blueprints:
            try:
                plan_parcial = self._crear_plan_desde_blueprints.ejecutar(especificacion, [blueprint])
            except Exception as exc:  # noqa: BLE001
                fallo = self._crear_fallo(exc=exc, codigo="CON-000", mensaje_usuario="No se pudo construir el índice de rutas")
                return None, "FAIL", "Error en preflight de conflictos", fallo.detalle_tecnico, fallo
            for ruta in plan_parcial.obtener_rutas():
                indice.setdefault(ruta, set()).add(blueprint)

        mapeo_conflictos = {ruta: sorted(list(duenios)) for ruta, duenios in indice.items() if len(duenios) > 1}
        if mapeo_conflictos:
            rutas = sorted(mapeo_conflictos.keys())
            conflicto = ConflictosFinalizacion(
                total_rutas_duplicadas=len(rutas),
                rutas_duplicadas=rutas,
                rutas_por_blueprint=mapeo_conflictos,
            )
            top = "\n".join(f"{ruta} -> [{', '.join(mapeo_conflictos[ruta])}]" for ruta in rutas[:5])
            mensaje_usuario = (
                "Se detectaron rutas duplicadas entre blueprints. "
                "Acción: desactiva uno de los blueprints que generan la misma ruta "
                "(p.ej. CRUD persona duplicado)"
            )
            exc = ErrorConflictoArchivos(f"Rutas duplicadas detectadas: {len(rutas)}")
            fallo = self._crear_fallo(exc=exc, codigo="CON-001", mensaje_usuario=mensaje_usuario, tipo_forzado=CONFLICTO)
            evidencia = (
                f"total rutas duplicadas: {len(rutas)}\n"
                "Ejemplos ruta -> [blueprints]:\n"
                f"{top}\n\n"
                "Recomendación: No selecciones más de 1 blueprint CRUD para la misma entidad.\n\n"
                f"{fallo.detalle_tecnico}"
            )
            return conflicto, "FAIL", "Rutas duplicadas detectadas", evidencia, fallo

        return None, "PASS", "Sin colisiones entre blueprints", "Sin rutas duplicadas", None

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
            fallo = self._crear_fallo(exc=exc, codigo="IO-002", mensaje_usuario="Falló la generación del proyecto en sandbox")
            return None, "FAIL", "Falló generación en sandbox", fallo.detalle_tecnico, fallo

        manifest = ruta_proyecto / "manifest.json"
        if not manifest.exists():
            exc = ErrorConflictoArchivos(f"manifest.json ausente: {manifest}")
            fallo = self._crear_fallo(exc=exc, codigo="CON-002", mensaje_usuario="No se generó manifest.json")
            return None, "FAIL", "manifest.json ausente", fallo.detalle_tecnico, fallo

        top_level = sorted([ruta.name for ruta in ruta_proyecto.iterdir()])
        evidencia = f"Top-level creado: {', '.join(top_level)}\nManifest: {manifest}"
        return None, "PASS", "Proyecto generado", evidencia, None

    def _auditar_arquitectura(self, ruta_proyecto: Path):
        resultado = self._auditor_arquitectura.auditar(str(ruta_proyecto))
        hallazgos = list(resultado.errores) + list(resultado.warnings)
        evidencia = "\n".join(hallazgos[:5]) if hallazgos else "Sin hallazgos"
        estado = "PASS" if resultado.valido else "FAIL"
        if estado == "FAIL":
            exc = ErrorAplicacion("La auditoría de arquitectura encontró hallazgos")
            fallo = self._crear_fallo(exc=exc, codigo="VAL-900", mensaje_usuario="Corrige hallazgos de arquitectura antes de continuar")
            return None, estado, f"Hallazgos: {len(hallazgos)}", f"{evidencia}\n\n{fallo.detalle_tecnico}", fallo
        return None, estado, f"Hallazgos: {len(hallazgos)}", evidencia, None

    def _smoke_test(self, ruta_proyecto: Path):
        compileall = self._ejecutor_procesos.ejecutar(["python", "-m", "compileall", "."], cwd=str(ruta_proyecto))
        evidencia = [
            f"compileall exit={compileall.codigo_salida}",
            (compileall.stdout or compileall.stderr)[:1000],
        ]
        if compileall.codigo_salida != 0:
            exc = OSError("compileall falló")
            fallo = self._crear_fallo(exc=exc, codigo="IO-010", mensaje_usuario="El código generado no compila correctamente")
            evidencia.append(fallo.detalle_tecnico)
            return None, "FAIL", "compileall falló", "\n".join(evidencia), fallo

        hay_tests = (ruta_proyecto / "pytest.ini").exists() or (ruta_proyecto / "tests").exists()
        if not hay_tests:
            evidencia.append("pytest SKIP (sin tests)")
            return None, "SKIP", "Sin tests generados", "\n".join(evidencia), None

        pytest_res = self._ejecutor_procesos.ejecutar(["pytest", "-q", "--maxfail=1"], cwd=str(ruta_proyecto))
        evidencia.extend([f"pytest exit={pytest_res.codigo_salida}", (pytest_res.stdout or pytest_res.stderr)[:1000]])
        if pytest_res.codigo_salida != 0:
            exc = ErrorAplicacion("pytest falló")
            fallo = self._crear_fallo(exc=exc, codigo="VAL-901", mensaje_usuario="Revisa los tests generados y corrige el blueprint")
            evidencia.append(fallo.detalle_tecnico)
            return None, "FAIL", "pytest falló", "\n".join(evidencia), fallo
        return None, "PASS", "compileall y pytest OK", "\n".join(evidencia), None

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

    def _existe_clase_persona(self, clases: list[EspecificacionClase]) -> bool:
        return any(clase.nombre.casefold() == "persona" for clase in clases)

    def _crear_fallo(self, exc: Exception, codigo: str, mensaje_usuario: str, tipo_forzado: str | None = None) -> _FalloEtapa:
        tipo = tipo_forzado or self._clasificar_fallo(exc)
        detalle = self._detalle_tecnico(exc)
        return _FalloEtapa(tipo_fallo=tipo, codigo=codigo, mensaje_usuario=mensaje_usuario, detalle_tecnico=detalle)

    def _clasificar_fallo(self, exc: Exception) -> str:
        if isinstance(exc, (ErrorValidacion, ErrorValidacionDominio)):
            return VALIDACION
        if isinstance(exc, ErrorConflictoArchivos):
            return CONFLICTO
        if isinstance(exc, OSError):
            return IO
        return INESPERADO

    def _detalle_tecnico(self, exc: Exception) -> str:
        origen = self._origen_excepcion(exc.__traceback__)
        linea_raise = self._linea_raise(exc.__traceback__)
        stack = traceback.format_exception(type(exc), exc, exc.__traceback__)
        stack_lineas_completas = "".join(stack).splitlines()
        stack_lineas = stack_lineas_completas[-40:]
        stacktrace = "\n".join(stack_lineas)
        return (
            f"excepcion_tipo: {type(exc).__name__}\n"
            f"excepcion_mensaje: {exc}\n"
            f"origen: {origen}\n"
            f"linea_raise: {linea_raise}\n"
            f"stacktrace_recortado:\n{stacktrace}"
        )

    def _origen_excepcion(self, traza: TracebackType | None) -> str:
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

    def _warnings_incompatibilidades(self, blueprints: list[str]) -> list[str]:
        seleccion = set(blueprints)
        warnings: list[str] = []
        for izquierda, derecha, mensaje in self._INCOMPATIBILIDADES_DECLARATIVAS:
            if izquierda in seleccion and derecha in seleccion:
                warnings.append(mensaje)
        return warnings

    def _serializar_warnings(self, warnings: list[str]) -> str:
        if not warnings:
            return ""
        listado = "\n".join(f"- {warning}" for warning in warnings)
        return f"Warnings declarativos:\n{listado}"

    def _anexar_etapas_skip(self, etapas: list[ResultadoEtapa], motivo: str) -> None:
        etapas.extend(
            [
                ResultadoEtapa("Generación sandbox", "SKIP", 0, f"No ejecutada por {motivo}"),
                ResultadoEtapa("Auditoría arquitectura", "SKIP", 0, f"No ejecutada por {motivo}"),
                ResultadoEtapa("Smoke test", "SKIP", 0, f"No ejecutada por {motivo}"),
            ]
        )

    def _completar_evidencias_skip(self, evidencias: dict[str, str]) -> None:
        evidencias.setdefault("generacion_sandbox", "No ejecutada")
        evidencias.setdefault("auditoria_arquitectura", "No ejecutada")
        evidencias.setdefault("smoke_test", "No ejecutada")

    def _registrar_incidente_si_aplica(self, etapa: ResultadoEtapa, evidencias: dict[str, str], id_ejecucion: str) -> None:
        if etapa.estado != "FAIL":
            return
        if etapa.tipo_fallo == INESPERADO:
            evidencias["incidente_id"] = id_ejecucion

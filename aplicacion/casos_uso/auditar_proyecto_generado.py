"""Caso de uso para auditar estructura, arquitectura y cobertura de un proyecto generado."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import logging
from pathlib import Path
import re

from aplicacion.casos_uso.auditoria.validadores import ContextoAuditoria, ValidadorAuditoria, ValidadorImports
from aplicacion.errores import ErrorAuditoria, ErrorInfraestructura
from aplicacion.puertos.calculadora_hash_puerto import CalculadoraHashPuerto
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos
from aplicacion.validacion import MotorValidacion, ReglaValidacion, ResultadoValidacion
from dominio.errores import ErrorDominio

LOGGER = logging.getLogger(__name__)


@dataclass
class ResultadoAuditoria:
    """Resultado detallado de la auditoría del proyecto generado."""

    valido: bool
    lista_errores: list[str] = field(default_factory=list)
    cobertura: float | None = None
    resumen: str = ""


@dataclass(frozen=True)
class ResultadoComando:
    codigo_salida: int
    stdout: str
    stderr: str


@dataclass
class _EstadoAuditoria:
    errores: list[str]
    blueprints: list[str]
    resultado_pytest: ResultadoComando = field(
        default_factory=lambda: ResultadoComando(codigo_salida=1, stdout="No ejecutado", stderr="")
    )
    cobertura: float | None = None
    conclusion: str = "RECHAZADO"


class _CalculadoraHashLocal:
    """Fallback temporal para evitar dependencia directa de infraestructura."""

    def calcular_hash_archivo(self, ruta: Path) -> str:
        digestor = hashlib.sha256()
        with open(ruta, "rb") as archivo:
            for bloque in iter(lambda: archivo.read(8192), b""):
                digestor.update(bloque)
        return digestor.hexdigest()


@dataclass(frozen=True)
class _ContextoReglasAuditoria:
    base: Path
    blueprints: list[str]
    estructura_requerida: list[str]
    validadores: list[ValidadorAuditoria]
    calculadora_hash: CalculadoraHashPuerto


class _ReglaRecursoObligatorio(ReglaValidacion):
    def __init__(self, ruta_relativa: str, mensaje_error: str) -> None:
        self._ruta_relativa = ruta_relativa
        self._mensaje_error = mensaje_error

    def validar(self, contexto: _ContextoReglasAuditoria) -> ResultadoValidacion | None:
        if (contexto.base / self._ruta_relativa).exists():
            return None
        return ResultadoValidacion(False, self._mensaje_error, "ERROR")


class _ReglaValidadorArquitecturaIndividual(ReglaValidacion):
    def __init__(self, validador: ValidadorAuditoria) -> None:
        self._validador = validador

    def validar(self, contexto: _ContextoReglasAuditoria) -> ResultadoValidacion | None:
        auditoria = ContextoAuditoria(base=contexto.base)
        resultado = self._validador.validar(auditoria)
        if not resultado.errores:
            return None
        return ResultadoValidacion(False, resultado.errores[0], "ERROR")


class _ReglaDependenciasInformes(ReglaValidacion):
    def validar(self, contexto: _ContextoReglasAuditoria) -> ResultadoValidacion | None:
        if not any(nombre in {"export_excel", "export_pdf"} for nombre in contexto.blueprints):
            return None
        ruta = contexto.base / "requirements.txt"
        if not ruta.exists():
            return ResultadoValidacion(False, "No existe requirements.txt y se solicitaron blueprints de informes.", "ERROR")
        contenido = ruta.read_text(encoding="utf-8").lower()
        faltantes: list[str] = []
        if "openpyxl" not in contenido:
            faltantes.append("openpyxl")
        if "reportlab" not in contenido:
            faltantes.append("reportlab")
        if faltantes:
            dependencias = ", ".join(faltantes)
            return ResultadoValidacion(False, f"requirements.txt no incluye dependencias requeridas para informes: {dependencias}.", "ERROR")
        return None


class _ReglaConsistenciaManifest(ReglaValidacion):
    def validar(self, contexto: _ContextoReglasAuditoria) -> ResultadoValidacion | None:
        ruta_manifest = contexto.base / "manifest.json"
        if not ruta_manifest.exists():
            return None
        payload = json.loads(ruta_manifest.read_text(encoding="utf-8"))
        for entrada in payload.get("archivos", []):
            error = self._validar_entrada_manifest(contexto, entrada)
            if error is not None:
                return ResultadoValidacion(False, error, "ERROR")
        return None

    def _validar_entrada_manifest(self, contexto: _ContextoReglasAuditoria, entrada: dict[str, str]) -> str | None:
        ruta_relativa = entrada.get("ruta_relativa", "")
        hash_esperado = entrada.get("hash_sha256", "")
        if not ruta_relativa or not hash_esperado:
            return "manifest.json contiene entradas incompletas."
        ruta_archivo = contexto.base / ruta_relativa
        if not ruta_archivo.exists():
            return f"manifest.json referencia archivo inexistente: {ruta_relativa}"
        hash_actual = contexto.calculadora_hash.calcular_hash_archivo(ruta_archivo)
        if hash_actual != hash_esperado:
            return f"Hash inconsistente para {ruta_relativa} en manifest.json"
        return None


class AuditarProyectoGenerado:
    """Verifica reglas de calidad para el proyecto generado."""

    ESTRUCTURA_REQUERIDA = [
        "dominio",
        "aplicacion",
        "infraestructura",
        "presentacion",
        "tests",
        "scripts",
        "logs",
        "docs",
        "VERSION",
        "CHANGELOG.md",
    ]

    def __init__(
        self,
        ejecutor_procesos: EjecutorProcesos,
        calculadora_hash: CalculadoraHashPuerto | None = None,
    ) -> None:
        self._ejecutor_procesos = ejecutor_procesos
        self._calculadora_hash = calculadora_hash or _CalculadoraHashLocal()
        self._validadores_auditoria = self._crear_validadores_auditoria()
        self._motor_validacion = MotorValidacion(self._crear_reglas_base())

    def _crear_validadores_auditoria(self) -> list[ValidadorAuditoria]:
        return [ValidadorImports()]

    def _crear_reglas_base(self) -> list[ReglaValidacion]:
        reglas: list[ReglaValidacion] = []
        for recurso in self.ESTRUCTURA_REQUERIDA:
            reglas.append(_ReglaRecursoObligatorio(recurso, f"No existe el recurso obligatorio: {recurso}"))
        for validador in self._validadores_auditoria:
            reglas.append(_ReglaValidadorArquitecturaIndividual(validador))
        reglas.extend(
            [
                _ReglaRecursoObligatorio(
                    "infraestructura/logging_config.py",
                    "No existe configuración de logging en infraestructura/logging_config.py",
                ),
                _ReglaRecursoObligatorio("logs/seguimiento.log", "No existe logs/seguimiento.log"),
                _ReglaRecursoObligatorio("logs/crashes.log", "No existe logs/crashes.log"),
                _ReglaDependenciasInformes(),
                _ReglaConsistenciaManifest(),
            ]
        )
        return reglas

    def ejecutar(self, ruta_proyecto: str, blueprints_usados: list[str] | None = None) -> ResultadoAuditoria:
        """Ejecuta las validaciones obligatorias sobre un proyecto ya generado."""
        base = self._construir_base_proyecto(ruta_proyecto)
        estado = self._crear_estado_auditoria(blueprints_usados)
        LOGGER.info("Inicio auditoría avanzada proyecto=%s", ruta_proyecto)

        try:
            self._validar_reglas_base(base, estado)
            self._ejecutar_pytest_y_cobertura(base, estado)
            self._registrar_resumen_auditoria(estado)
            return self._construir_resultado_auditoria(estado)
        except ErrorDominio:
            raise
        except (ErrorInfraestructura, OSError, ValueError, RuntimeError) as exc:
            LOGGER.error("Fallo técnico en auditoría: %s", exc, exc_info=True)
            estado.errores.append(f"Error de auditoría: {exc}")
            raise ErrorAuditoria(f"No fue posible completar la auditoría: {exc}") from exc
        finally:
            self._escribir_informe(
                base=base,
                blueprints=estado.blueprints,
                errores=estado.errores,
                cobertura=estado.cobertura,
                resultado_pytest=estado.resultado_pytest,
                conclusion=estado.conclusion,
            )

    def _construir_base_proyecto(self, ruta_proyecto: str) -> Path:
        return Path(ruta_proyecto)

    def _crear_estado_auditoria(self, blueprints_usados: list[str] | None) -> _EstadoAuditoria:
        return _EstadoAuditoria(errores=[], blueprints=blueprints_usados or [])

    def _validar_reglas_base(self, base: Path, estado: _EstadoAuditoria) -> None:
        self._motor_validacion = MotorValidacion(self._crear_reglas_base())
        contexto = _ContextoReglasAuditoria(
            base=base,
            blueprints=estado.blueprints,
            estructura_requerida=self.ESTRUCTURA_REQUERIDA,
            validadores=self._validadores_auditoria,
            calculadora_hash=self._calculadora_hash,
        )
        for resultado in self._motor_validacion.ejecutar(contexto):
            if resultado.severidad == "ERROR" and not resultado.exito and resultado.mensaje:
                estado.errores.append(resultado.mensaje)

    def _ejecutar_pytest_y_cobertura(self, base: Path, estado: _EstadoAuditoria) -> None:
        estado.resultado_pytest = self._ejecutor_procesos.ejecutar(
            comando=["pytest", "--cov=.", "--cov-report=term"],
            cwd=str(base),
        )
        estado.cobertura = self._extraer_cobertura_total(estado.resultado_pytest.stdout)
        if estado.cobertura is None:
            estado.errores.append("No fue posible extraer el porcentaje total de cobertura de pytest.")
        elif estado.cobertura < 85.0:
            estado.errores.append(f"Cobertura insuficiente: {estado.cobertura:.2f}% (mínimo requerido: 85%).")

        if estado.resultado_pytest.codigo_salida != 0 and estado.cobertura is None:
            estado.errores.append("La ejecución de pytest finalizó con error y sin reporte de cobertura usable.")

    def _registrar_resumen_auditoria(self, estado: _EstadoAuditoria) -> None:
        LOGGER.info("Cobertura total detectada: %s", estado.cobertura)
        LOGGER.info("Errores de auditoría detectados: %s", estado.errores)

    def _construir_resultado_auditoria(self, estado: _EstadoAuditoria) -> ResultadoAuditoria:
        valido = not estado.errores
        estado.conclusion = "APROBADO" if valido else "RECHAZADO"
        resumen = (
            f"Auditoría {estado.conclusion}. "
            f"Errores: {len(estado.errores)}. "
            f"Cobertura: {f'{estado.cobertura:.2f}%' if estado.cobertura is not None else 'no disponible'}."
        )
        return ResultadoAuditoria(
            valido=valido,
            lista_errores=estado.errores,
            cobertura=estado.cobertura,
            resumen=resumen,
        )

    def _extraer_cobertura_total(self, salida: str) -> float | None:
        coincidencias = re.findall(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", salida)
        if not coincidencias:
            return None
        return float(coincidencias[-1])

    def _escribir_informe(
        self,
        base: Path,
        blueprints: list[str],
        errores: list[str],
        cobertura: float | None,
        resultado_pytest: ResultadoComando,
        conclusion: str,
    ) -> None:
        ruta_docs = base / "docs"
        ruta_docs.mkdir(parents=True, exist_ok=True)
        ruta_informe = ruta_docs / "informe_auditoria.md"

        estructura_ok = "OK" if not any("recurso obligatorio" in e for e in errores) else "ERROR"
        arquitectura_ok = "OK" if not any("Import" in e or "circular" in e for e in errores) else "ERROR"
        logging_ok = "OK" if not any("logging" in e or "logs/" in e for e in errores) else "ERROR"
        manifest_ok = "OK" if not any("manifest" in e or "Hash" in e for e in errores) else "ERROR"

        contenido = (
            "# Informe de Auditoría\n\n"
            "## Fecha\n"
            f"{datetime.now().isoformat(timespec='seconds')}\n\n"
            "## Blueprints usados\n"
            f"{', '.join(blueprints) if blueprints else 'No informado'}\n\n"
            "## Validación de estructura\n"
            f"Resultado: {estructura_ok}\n\n"
            "## Validación de arquitectura (imports)\n"
            f"Resultado: {arquitectura_ok}\n\n"
            "## Validación logging\n"
            f"Resultado: {logging_ok}\n\n"
            "## Consistencia manifest/hash\n"
            f"Resultado: {manifest_ok}\n\n"
            "## Resultado pytest\n"
            f"Código de salida: {resultado_pytest.codigo_salida}\n\n"
            "```\n"
            f"{resultado_pytest.stdout.strip()}\n"
            "```\n\n"
            "## Cobertura total\n"
            f"{f'{cobertura:.2f}%' if cobertura is not None else 'No disponible'}\n\n"
            "## Conclusión final (APROBADO / RECHAZADO)\n"
            f"{conclusion}\n\n"
        )

        if errores:
            contenido += "### Errores detectados\n\n"
            for error in errores:
                contenido += f"- {error}\n"

        ruta_informe.write_text(contenido, encoding="utf-8")

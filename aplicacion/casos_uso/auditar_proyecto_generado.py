"""Caso de uso para auditar estructura, arquitectura y cobertura de un proyecto generado."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
from pathlib import Path

from aplicacion.casos_uso.auditoria.generador_reporte_auditoria import GeneradorReporteAuditoria
from aplicacion.casos_uso.auditoria.validador_estructura import ValidadorEstructura
from aplicacion.casos_uso.auditoria.verificador_hashes import CalculadoraHashInterna, VerificadorHashes
from aplicacion.errores import ErrorAuditoria
from aplicacion.puertos.calculadora_hash import CalculadoraHash
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos

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


class AuditarProyectoGenerado:
    """Verifica reglas de calidad para el proyecto generado."""

    def __init__(
        self,
        ejecutor_procesos: EjecutorProcesos,
        calculadora_hash: CalculadoraHash | None = None,
        validador_estructura: ValidadorEstructura | None = None,
        verificador_hashes: VerificadorHashes | None = None,
        generador_reporte: GeneradorReporteAuditoria | None = None,
    ) -> None:
        self._ejecutor_procesos = ejecutor_procesos
        self._validador_estructura = validador_estructura or ValidadorEstructura()
        self._verificador_hashes = verificador_hashes or VerificadorHashes(calculadora_hash or CalculadoraHashInterna())
        self._generador_reporte = generador_reporte or GeneradorReporteAuditoria()

    def ejecutar(self, ruta_proyecto: str, blueprints_usados: list[str] | None = None) -> ResultadoAuditoria:
        """Ejecuta las validaciones obligatorias sobre un proyecto ya generado."""
        base = Path(ruta_proyecto)
        errores: list[str] = []
        blueprints = blueprints_usados or []
        resultado_pytest = ResultadoComando(codigo_salida=1, stdout="No ejecutado", stderr="")
        cobertura: float | None = None
        conclusion = "RECHAZADO"
        LOGGER.info("Inicio auditoría avanzada proyecto=%s", ruta_proyecto)

        try:
            errores.extend(self._validador_estructura.validar_estructura(base))
            errores.extend(self._validador_estructura.validar_imports(base))
            errores.extend(self._validador_estructura.validar_logging(base))
            errores.extend(self._validador_estructura.validar_dependencias_informes(base, blueprints))
            errores.extend(self._validar_consistencia_manifest(base))

            resultado_pytest = self._ejecutor_procesos.ejecutar(
                comando=["pytest", "--cov=.", "--cov-report=term"],
                cwd=str(base),
            )
            cobertura = self._validador_estructura.extraer_cobertura_total(resultado_pytest.stdout)
            if cobertura is None:
                errores.append("No fue posible extraer el porcentaje total de cobertura de pytest.")
            elif cobertura < 85.0:
                errores.append(f"Cobertura insuficiente: {cobertura:.2f}% (mínimo requerido: 85%).")

            if resultado_pytest.codigo_salida != 0 and cobertura is None:
                errores.append("La ejecución de pytest finalizó con error y sin reporte de cobertura usable.")

            valido = not errores
            conclusion = "APROBADO" if valido else "RECHAZADO"
            resumen = (
                f"Auditoría {conclusion}. "
                f"Errores: {len(errores)}. "
                f"Cobertura: {f'{cobertura:.2f}%' if cobertura is not None else 'no disponible'}."
            )
            return ResultadoAuditoria(valido=valido, lista_errores=errores, cobertura=cobertura, resumen=resumen)
        except Exception as exc:
            LOGGER.error("Fallo inesperado en auditoría: %s", exc, exc_info=True)
            raise ErrorAuditoria(f"No fue posible completar la auditoría: {exc}") from exc
        finally:
            self._generador_reporte.escribir(
                base=base,
                blueprints=blueprints,
                errores=errores,
                cobertura=cobertura,
                codigo_salida_pytest=resultado_pytest.codigo_salida,
                stdout_pytest=resultado_pytest.stdout,
                conclusion=conclusion,
            )

    def _validar_consistencia_manifest(self, base: Path) -> list[str]:
        ruta_manifest = base / "manifest.json"
        if not ruta_manifest.exists():
            return []
        payload = self._validador_estructura.cargar_json(ruta_manifest)
        return self._verificador_hashes.validar_consistencia_manifest(base, payload)

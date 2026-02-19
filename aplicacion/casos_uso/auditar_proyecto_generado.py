"""Caso de uso para auditar estructura, arquitectura y cobertura de un proyecto generado."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import logging
from pathlib import Path
import re

from aplicacion.errores import ErrorAuditoria, ErrorInfraestructura
from aplicacion.puertos.calculadora_hash_puerto import CalculadoraHashPuerto
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos
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


class _CalculadoraHashLocal:
    """Fallback temporal para evitar dependencia directa de infraestructura."""

    def calcular_hash_archivo(self, ruta: Path) -> str:
        digestor = hashlib.sha256()
        with open(ruta, "rb") as archivo:
            for bloque in iter(lambda: archivo.read(8192), b""):
                digestor.update(bloque)
        return digestor.hexdigest()


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
            errores.extend(self._validar_estructura(base))
            errores.extend(self._validar_imports(base))
            errores.extend(self._validar_logging(base))
            errores.extend(self._validar_dependencias_informes(base, blueprints))
            errores.extend(self._validar_consistencia_manifest(base))

            resultado_pytest = self._ejecutor_procesos.ejecutar(
                comando=["pytest", "--cov=.", "--cov-report=term"],
                cwd=str(base),
            )
            cobertura = self._extraer_cobertura_total(resultado_pytest.stdout)
            if cobertura is None:
                errores.append("No fue posible extraer el porcentaje total de cobertura de pytest.")
            elif cobertura < 85.0:
                errores.append(f"Cobertura insuficiente: {cobertura:.2f}% (mínimo requerido: 85%).")

            if resultado_pytest.codigo_salida != 0 and cobertura is None:
                errores.append("La ejecución de pytest finalizó con error y sin reporte de cobertura usable.")

            LOGGER.info("Cobertura total detectada: %s", cobertura)
            LOGGER.info("Errores de auditoría detectados: %s", errores)

            valido = not errores
            conclusion = "APROBADO" if valido else "RECHAZADO"
            resumen = (
                f"Auditoría {conclusion}. "
                f"Errores: {len(errores)}. "
                f"Cobertura: {f'{cobertura:.2f}%' if cobertura is not None else 'no disponible'}."
            )
            return ResultadoAuditoria(
                valido=valido,
                lista_errores=errores,
                cobertura=cobertura,
                resumen=resumen,
            )
        except ErrorDominio:
            raise
        except (ErrorInfraestructura, OSError, ValueError, RuntimeError) as exc:
            LOGGER.error("Fallo técnico en auditoría: %s", exc, exc_info=True)
            errores.append(f"Error de auditoría: {exc}")
            raise ErrorAuditoria(f"No fue posible completar la auditoría: {exc}") from exc
        finally:
            self._escribir_informe(
                base=base,
                blueprints=blueprints,
                errores=errores,
                cobertura=cobertura,
                resultado_pytest=resultado_pytest,
                conclusion=conclusion,
            )

    def _validar_estructura(self, base: Path) -> list[str]:
        LOGGER.info("Evaluando reglas de estructura")
        errores: list[str] = []
        for relativo in self.ESTRUCTURA_REQUERIDA:
            if not (base / relativo).exists():
                errores.append(f"No existe el recurso obligatorio: {relativo}")
        return errores

    def _validar_imports(self, base: Path) -> list[str]:
        LOGGER.info("Evaluando reglas de arquitectura por imports")
        errores: list[str] = []
        modulos_estandar_restringidos = {"json", "sqlite3"}
        modulos_exportacion = {"openpyxl", "reportlab"}
        prefijos_externos = {"pydantic", "requests", "sqlalchemy", "fastapi", "pyside6"}
        patron_import = re.compile(r"^\s*import\s+([a-zA-Z0-9_\.]+)", re.MULTILINE)
        patron_from = re.compile(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+", re.MULTILINE)
        grafo_imports: dict[str, set[str]] = {}

        for ruta_archivo in base.rglob("*.py"):
            relativo = ruta_archivo.relative_to(base)
            modulo_actual = self._ruta_a_modulo(relativo)
            contenido = ruta_archivo.read_text(encoding="utf-8")
            imports = set(patron_import.findall(contenido)) | set(patron_from.findall(contenido))
            grafo_imports[modulo_actual] = imports
            if not relativo.parts:
                continue

            for modulo in imports:
                modulo_raiz = modulo.lower().split(".")[0]
                if modulo_raiz == "sqlite3" and relativo.parts[0] != "infraestructura":
                    errores.append(f"Import sqlite3 fuera de infraestructura ({relativo}): {modulo}")
                if modulo_raiz in modulos_exportacion and relativo.parts[0] != "infraestructura":
                    errores.append(f"Import {modulo_raiz} fuera de infraestructura ({relativo}): {modulo}")

            if relativo.parts[0] == "dominio":
                for modulo in imports:
                    modulo_bajo = modulo.lower()
                    if modulo_bajo.startswith("infraestructura"):
                        errores.append(f"Import prohibido en dominio ({relativo}): {modulo}")
                    if modulo_bajo.startswith("presentacion"):
                        errores.append(f"Import prohibido en dominio ({relativo}): {modulo}")
                    if modulo_bajo.startswith("pyside6"):
                        errores.append(f"Import prohibido en dominio ({relativo}): {modulo}")
                    if modulo_bajo.split(".")[0] in modulos_estandar_restringidos:
                        errores.append(f"Import prohibido en dominio ({relativo}): {modulo}")
                    if modulo_bajo.split(".")[0] in prefijos_externos:
                        errores.append(f"Import externo no permitido en dominio ({relativo}): {modulo}")
            elif relativo.parts[0] == "aplicacion":
                for modulo in imports:
                    if modulo.lower().startswith("presentacion"):
                        errores.append(f"Import prohibido en aplicación ({relativo}): {modulo}")
            elif relativo.parts[0] == "presentacion":
                for modulo in imports:
                    if modulo.lower().startswith("infraestructura"):
                        errores.append(f"Import prohibido en presentación ({relativo}): {modulo}")

        errores.extend(self._detectar_ciclos_basicos(grafo_imports))
        return errores

    def _validar_dependencias_informes(self, base: Path, blueprints: list[str]) -> list[str]:
        blueprints_informes = {"export_excel", "export_pdf"}
        if not any(nombre in blueprints_informes for nombre in blueprints):
            return []

        ruta_requirements = base / "requirements.txt"
        if not ruta_requirements.exists():
            return ["No existe requirements.txt y se solicitaron blueprints de informes."]

        contenido = ruta_requirements.read_text(encoding="utf-8").lower()
        errores: list[str] = []
        if "openpyxl" not in contenido:
            errores.append("requirements.txt no incluye openpyxl para exportación Excel.")
        if "reportlab" not in contenido:
            errores.append("requirements.txt no incluye reportlab para exportación PDF.")
        return errores

    def _validar_consistencia_manifest(self, base: Path) -> list[str]:
        ruta_manifest = base / "manifest.json"
        if not ruta_manifest.exists():
            return []
        payload = json.loads(ruta_manifest.read_text(encoding="utf-8"))
        errores: list[str] = []
        for entrada in payload.get("archivos", []):
            ruta_relativa = entrada.get("ruta_relativa", "")
            hash_esperado = entrada.get("hash_sha256", "")
            if not ruta_relativa or not hash_esperado:
                errores.append("manifest.json contiene entradas incompletas.")
                continue
            ruta_archivo = base / ruta_relativa
            if not ruta_archivo.exists():
                errores.append(f"manifest.json referencia archivo inexistente: {ruta_relativa}")
                continue
            hash_actual = self._calculadora_hash.calcular_hash_archivo(ruta_archivo)
            if hash_actual != hash_esperado:
                errores.append(f"Hash inconsistente para {ruta_relativa} en manifest.json")
        return errores

    def _detectar_ciclos_basicos(self, grafo_imports: dict[str, set[str]]) -> list[str]:
        errores: list[str] = []
        for modulo, dependencias in grafo_imports.items():
            for dependencia in dependencias:
                if dependencia in grafo_imports and modulo in grafo_imports.get(dependencia, set()):
                    errores.append(f"Import circular detectado entre {modulo} y {dependencia}")
        return sorted(set(errores))

    def _validar_logging(self, base: Path) -> list[str]:
        LOGGER.info("Evaluando reglas de logging")
        errores: list[str] = []
        if not (base / "infraestructura" / "logging_config.py").exists():
            errores.append("No existe configuración de logging en infraestructura/logging_config.py")
        if not (base / "logs" / "seguimiento.log").exists():
            errores.append("No existe logs/seguimiento.log")
        if not (base / "logs" / "crashes.log").exists():
            errores.append("No existe logs/crashes.log")
        return errores

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

    def _ruta_a_modulo(self, relativa: Path) -> str:
        sin_sufijo = relativa.with_suffix("")
        return ".".join(sin_sufijo.parts)

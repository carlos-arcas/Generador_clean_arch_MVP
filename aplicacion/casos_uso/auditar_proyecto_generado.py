"""Caso de uso para auditar estructura, arquitectura y cobertura de un proyecto generado."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import logging
from pathlib import Path
import re

from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos

LOGGER = logging.getLogger(__name__)


@dataclass
class ResultadoAuditoria:
    """Resultado detallado de la auditoría del proyecto generado."""

    valido: bool
    lista_errores: list[str] = field(default_factory=list)
    cobertura: float | None = None
    resumen: str = ""


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

    def __init__(self, ejecutor_procesos: EjecutorProcesos) -> None:
        self._ejecutor_procesos = ejecutor_procesos

    def ejecutar(self, ruta_proyecto: str, blueprints_usados: list[str] | None = None) -> ResultadoAuditoria:
        """Ejecuta las validaciones obligatorias sobre un proyecto ya generado."""
        base = Path(ruta_proyecto)
        errores: list[str] = []
        blueprints = blueprints_usados or []
        LOGGER.info("Inicio auditoría avanzada proyecto=%s", ruta_proyecto)

        errores.extend(self._validar_estructura(base))
        errores.extend(self._validar_imports(base))
        errores.extend(self._validar_logging(base))

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

        self._escribir_informe(
            base=base,
            blueprints=blueprints,
            errores=errores,
            cobertura=cobertura,
            resultado_pytest=resultado_pytest,
            conclusion=conclusion,
        )

        LOGGER.info("Conclusión final de auditoría: %s", conclusion)
        return ResultadoAuditoria(valido=valido, lista_errores=errores, cobertura=cobertura, resumen=resumen)

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

            for modulo in imports:
                modulo_raiz = modulo.lower().split(".")[0]
                if modulo_raiz == "sqlite3" and relativo.parts[0] != "infraestructura":
                    errores.append(
                        f"Import sqlite3 fuera de infraestructura ({relativo}): {modulo}"
                    )

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
                        errores.append(
                            f"Import prohibido en presentación ({relativo}): {modulo}"
                        )

        errores.extend(self._detectar_ciclos_basicos(grafo_imports))
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
        resultado_pytest,
        conclusion: str,
    ) -> None:
        ruta_docs = base / "docs"
        ruta_docs.mkdir(parents=True, exist_ok=True)
        ruta_informe = ruta_docs / "informe_auditoria.md"

        estructura_ok = "OK" if not any("recurso obligatorio" in e for e in errores) else "ERROR"
        arquitectura_ok = "OK" if not any("Import" in e or "circular" in e for e in errores) else "ERROR"
        logging_ok = "OK" if not any("logging" in e or "logs/" in e for e in errores) else "ERROR"

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

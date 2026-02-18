"""Auditor automático post-generación para proyectos Clean Architecture."""

from __future__ import annotations

import logging
from pathlib import Path
import re
import subprocess

from aplicacion.casos_uso.auditoria.generador_reporte_auditoria import (
    GeneradorReporteAuditoria,
    ResultadoAuditoria,
)
from aplicacion.casos_uso.auditoria.validador_estructura import ValidadorEstructura
from aplicacion.casos_uso.auditoria.verificador_hashes import VerificadorHashes

LOGGER = logging.getLogger(__name__)


class AuditarProyectoGenerado:
    """Orquesta validaciones de estructura, integridad y dependencias por capas."""

    def __init__(
        self,
        ejecutar_pytest: bool = False,
        validador_estructura: ValidadorEstructura | None = None,
        verificador_hashes: VerificadorHashes | None = None,
        generador_reporte: GeneradorReporteAuditoria | None = None,
    ) -> None:
        self._ejecutar_pytest = ejecutar_pytest
        self._validador_estructura = validador_estructura or ValidadorEstructura()
        self._verificador_hashes = verificador_hashes or VerificadorHashes()
        self._generador_reporte = generador_reporte or GeneradorReporteAuditoria()

    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        """Ejecuta la auditoría del proyecto generado."""
        base = Path(ruta_proyecto)
        errores: list[str] = []
        warnings: list[str] = []

        if not base.exists() or not base.is_dir():
            return self._generador_reporte.generar(
                errores=[f"La ruta '{ruta_proyecto}' no existe o no es un directorio."],
                warnings=[],
            )

        errores.extend(self._validador_estructura.validar(base))
        errores.extend(self._verificador_hashes.verificar(base))
        errores.extend(self._validar_dependencias_capas(base))

        if self._ejecutar_pytest:
            warnings.extend(self._ejecutar_pytest_opcional(base))

        LOGGER.info(
            "Auditoría post-generación finalizada: valido=%s errores=%s warnings=%s",
            len(errores) == 0,
            len(errores),
            len(warnings),
        )
        for error in errores:
            LOGGER.error("AUDIT ERROR: %s", error)
        for warning in warnings:
            LOGGER.warning("AUDIT WARNING: %s", warning)

        return self._generador_reporte.generar(errores=errores, warnings=warnings)

    def _validar_dependencias_capas(self, base: Path) -> list[str]:
        errores: list[str] = []
        patron_import = re.compile(r"^\s*import\s+([\w\.]+)", re.MULTILINE)
        patron_from = re.compile(r"^\s*from\s+([\w\.]+)\s+import\s+", re.MULTILINE)

        for archivo in base.rglob("*.py"):
            try:
                relativo = archivo.relative_to(base)
            except ValueError:
                continue
            if not relativo.parts:
                continue

            capa = relativo.parts[0]
            if capa not in {"dominio", "aplicacion"}:
                continue

            contenido = archivo.read_text(encoding="utf-8")
            imports = set(patron_import.findall(contenido)) | set(patron_from.findall(contenido))
            for modulo in imports:
                modulo_normalizado = modulo.lower()
                if capa == "dominio" and (
                    modulo_normalizado.startswith("infraestructura")
                    or modulo_normalizado.startswith("presentacion")
                ):
                    errores.append(f"Import prohibido en dominio ({relativo}): {modulo}")
                if capa == "aplicacion" and modulo_normalizado.startswith("presentacion"):
                    errores.append(f"Import prohibido en aplicacion ({relativo}): {modulo}")
        return errores

    def _ejecutar_pytest_opcional(self, base: Path) -> list[str]:
        try:
            resultado = subprocess.run(
                ["pytest", "-q"],
                cwd=base,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            return ["pytest no está disponible en el entorno; se omite validación opcional."]
        except Exception as exc:  # noqa: BLE001
            return [f"No se pudo ejecutar pytest de forma opcional: {exc}"]

        if resultado.returncode != 0:
            return [
                "pytest opcional reportó fallos en el proyecto generado.",
                resultado.stdout.strip() or resultado.stderr.strip() or "Sin salida adicional.",
            ]
        return []

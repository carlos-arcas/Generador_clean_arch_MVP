"""Auditor automático post-generación para proyectos Clean Architecture."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import subprocess

from aplicacion.casos_uso.auditoria.reglas_dependencias import (
    ReglaAplicacionNoDependeInfraestructura,
    ReglaDependencia,
    ReglaDominioNoDependeDeOtrasCapas,
    ReglaPresentacionNoDependeDominio,
)
from aplicacion.casos_uso.auditoria.validadores.validador_base import ContextoAuditoria

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResultadoAuditoria:
    """Resultado de la auditoría automática post-generación."""

    errores: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valido(self) -> bool:
        return not self.errores


class AuditarProyectoGenerado:
    """Valida estructura mínima e integridad básica del proyecto generado."""

    CARPETAS_OBLIGATORIAS = [
        "dominio",
        "aplicacion",
        "infraestructura",
        "presentacion",
        "tests",
        "docs",
        "logs",
        "configuracion",
        "scripts",
    ]

    ARCHIVOS_OBLIGATORIOS = [
        "VERSION",
        "CHANGELOG.md",
        "requirements.txt",
    ]

    def __init__(
        self,
        ejecutar_pytest: bool = False,
        reglas_dependencias: list[ReglaDependencia] | None = None,
    ) -> None:
        self._ejecutar_pytest = ejecutar_pytest
        self._reglas_dependencias = reglas_dependencias or [
            ReglaPresentacionNoDependeDominio(),
            ReglaAplicacionNoDependeInfraestructura(),
            ReglaDominioNoDependeDeOtrasCapas(),
        ]

    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        """Ejecuta la auditoría del proyecto generado."""
        base = Path(ruta_proyecto)
        errores: list[str] = []
        warnings: list[str] = []

        if not base.exists() or not base.is_dir():
            return ResultadoAuditoria(errores=[f"La ruta '{ruta_proyecto}' no existe o no es un directorio."])

        errores.extend(self._validar_estructura(base))
        errores.extend(self._validar_archivos(base))
        errores.extend(self._validar_manifest(base))
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

        return ResultadoAuditoria(errores=errores, warnings=warnings)

    def _validar_estructura(self, base: Path) -> list[str]:
        errores: list[str] = []
        for carpeta in self.CARPETAS_OBLIGATORIAS:
            if not (base / carpeta).is_dir():
                errores.append(f"No existe la carpeta obligatoria: {carpeta}")
        return errores

    def _validar_archivos(self, base: Path) -> list[str]:
        errores: list[str] = []
        for archivo in self.ARCHIVOS_OBLIGATORIOS:
            if not (base / archivo).is_file():
                errores.append(f"No existe el archivo obligatorio: {archivo}")
        return errores

    def _validar_manifest(self, base: Path) -> list[str]:
        candidatos = [base / "MANIFEST.json", base / "configuracion" / "MANIFEST.json", base / "manifest.json"]
        ruta_manifest = next((ruta for ruta in candidatos if ruta.exists()), None)
        if ruta_manifest is None:
            return ["No existe MANIFEST requerido: MANIFEST.json"]

        try:
            payload = json.loads(ruta_manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return [f"{ruta_manifest.name} no es un JSON válido: {exc}"]

        if not isinstance(payload, dict):
            return [f"{ruta_manifest.name} debe contener un objeto JSON en raíz."]

        return []

    def _validar_dependencias_capas(self, base: Path) -> list[str]:
        contexto = ContextoAuditoria(base=base)
        errores: list[str] = []
        for regla in self._reglas_dependencias:
            errores.extend(regla.evaluar(contexto).errores)
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
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            return [f"No se pudo ejecutar pytest de forma opcional: {exc}"]

        if resultado.returncode != 0:
            return [
                "pytest opcional reportó fallos en el proyecto generado.",
                resultado.stdout.strip() or resultado.stderr.strip() or "Sin salida adicional.",
            ]
        return []

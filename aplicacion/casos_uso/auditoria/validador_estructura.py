"""Validador de estructura base para auditoría post-generación."""

from __future__ import annotations

from pathlib import Path


class ValidadorEstructura:
    """Valida carpetas y archivos obligatorios del proyecto."""

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

    def validar(self, base: Path) -> list[str]:
        errores: list[str] = []
        for carpeta in self.CARPETAS_OBLIGATORIAS:
            if not (base / carpeta).is_dir():
                errores.append(f"No existe la carpeta obligatoria: {carpeta}")
        for archivo in self.ARCHIVOS_OBLIGATORIOS:
            if not (base / archivo).is_file():
                errores.append(f"No existe el archivo obligatorio: {archivo}")
        return errores

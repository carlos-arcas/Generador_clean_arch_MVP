"""Validaciones de estructura y reglas de import para auditoría CLI."""

from __future__ import annotations

import json
from pathlib import Path
import re


class ValidadorEstructura:
    """Encapsula reglas estructurales y de arquitectura por imports."""

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

    def validar_estructura(self, base: Path) -> list[str]:
        return [f"No existe el recurso obligatorio: {relativo}" for relativo in self.ESTRUCTURA_REQUERIDA if not (base / relativo).exists()]

    def validar_imports(self, base: Path) -> list[str]:
        errores: list[str] = []
        modulos_estandar_restringidos = {"json", "sqlite3"}
        modulos_exportacion = {"openpyxl", "reportlab"}
        prefijos_externos = {"pydantic", "requests", "sqlalchemy", "fastapi", "pyside6"}
        patron_import = re.compile(r"^\s*import\s+([a-zA-Z0-9_\.]+)", re.MULTILINE)
        patron_from = re.compile(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+", re.MULTILINE)
        grafo_imports: dict[str, set[str]] = {}

        for ruta_archivo in base.rglob("*.py"):
            relativo = ruta_archivo.relative_to(base)
            modulo_actual = self.ruta_a_modulo(relativo)
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

        errores.extend(self.detectar_ciclos_basicos(grafo_imports))
        return errores

    def validar_dependencias_informes(self, base: Path, blueprints: list[str]) -> list[str]:
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

    def validar_logging(self, base: Path) -> list[str]:
        errores: list[str] = []
        if not (base / "infraestructura" / "logging_config.py").exists():
            errores.append("No existe configuración de logging en infraestructura/logging_config.py")
        if not (base / "logs" / "seguimiento.log").exists():
            errores.append("No existe logs/seguimiento.log")
        if not (base / "logs" / "crashes.log").exists():
            errores.append("No existe logs/crashes.log")
        return errores

    def detectar_ciclos_basicos(self, grafo_imports: dict[str, set[str]]) -> list[str]:
        errores: list[str] = []
        for modulo, dependencias in grafo_imports.items():
            for dependencia in dependencias:
                if dependencia in grafo_imports and modulo in grafo_imports.get(dependencia, set()):
                    errores.append(f"Import circular detectado entre {modulo} y {dependencia}")
        return sorted(set(errores))

    def ruta_a_modulo(self, relativa: Path) -> str:
        return ".".join(relativa.with_suffix("").parts)

    def extraer_cobertura_total(self, salida: str) -> float | None:
        coincidencias = re.findall(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", salida)
        if not coincidencias:
            return None
        return float(coincidencias[-1])

    def cargar_json(self, ruta: Path) -> dict:
        return json.loads(ruta.read_text(encoding="utf-8"))

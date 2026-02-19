"""Validador de reglas de arquitectura basadas en imports."""

from __future__ import annotations

from pathlib import Path
import re

from aplicacion.casos_uso.auditoria.validadores.validador_base import (
    ContextoAuditoria,
    ResultadoValidacion,
    ValidadorAuditoria,
)


class ValidadorImports(ValidadorAuditoria):
    """Valida dependencias permitidas por capa usando imports Python."""

    _MODULOS_ESTANDAR_RESTRINGIDOS = {"json", "sqlite3"}
    _MODULOS_EXPORTACION = {"openpyxl", "reportlab"}
    _PREFIJOS_EXTERNOS = {"pydantic", "requests", "sqlalchemy", "fastapi", "pyside6"}

    def __init__(self) -> None:
        self._patron_import = re.compile(r"^\s*import\s+([a-zA-Z0-9_\.]+)", re.MULTILINE)
        self._patron_from = re.compile(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+", re.MULTILINE)

    def validar(self, contexto: ContextoAuditoria) -> ResultadoValidacion:
        errores: list[str] = []
        grafo_imports: dict[str, set[str]] = {}

        for ruta_archivo in contexto.base.rglob("*.py"):
            self._procesar_archivo(contexto.base, ruta_archivo, errores, grafo_imports)

        errores.extend(self._detectar_ciclos_basicos(grafo_imports))
        return ResultadoValidacion(exito=not errores, errores=errores)

    def _procesar_archivo(
        self,
        base: Path,
        ruta_archivo: Path,
        errores: list[str],
        grafo_imports: dict[str, set[str]],
    ) -> None:
        relativo = ruta_archivo.relative_to(base)
        modulo_actual = self._ruta_a_modulo(relativo)
        contenido = ruta_archivo.read_text(encoding="utf-8")
        imports = set(self._patron_import.findall(contenido)) | set(self._patron_from.findall(contenido))
        grafo_imports[modulo_actual] = imports
        if not relativo.parts:
            return

        self._validar_modulos_restringidos(relativo, imports, errores)
        capa = relativo.parts[0]
        if capa == "dominio":
            self._regla_imports_dominio(relativo, imports, errores)
            return
        if capa == "aplicacion":
            self._regla_imports_aplicacion(relativo, imports, errores)
            return
        if capa == "presentacion":
            self._regla_imports_presentacion(relativo, imports, errores)

    def _validar_modulos_restringidos(self, relativo: Path, imports: set[str], errores: list[str]) -> None:
        for modulo in imports:
            modulo_raiz = modulo.lower().split(".")[0]
            if modulo_raiz == "sqlite3" and relativo.parts[0] != "infraestructura":
                errores.append(f"Import sqlite3 fuera de infraestructura ({relativo}): {modulo}")
            if modulo_raiz in self._MODULOS_EXPORTACION and relativo.parts[0] != "infraestructura":
                errores.append(f"Import {modulo_raiz} fuera de infraestructura ({relativo}): {modulo}")

    def _regla_imports_dominio(self, relativo: Path, imports: set[str], errores: list[str]) -> None:
        for modulo in imports:
            modulo_bajo = modulo.lower()
            if modulo_bajo.startswith("infraestructura"):
                errores.append(f"Import prohibido en dominio ({relativo}): {modulo}")
            if modulo_bajo.startswith("presentacion"):
                errores.append(f"Import prohibido en dominio ({relativo}): {modulo}")
            if modulo_bajo.startswith("pyside6"):
                errores.append(f"Import prohibido en dominio ({relativo}): {modulo}")
            if modulo_bajo.split(".")[0] in self._MODULOS_ESTANDAR_RESTRINGIDOS:
                errores.append(f"Import prohibido en dominio ({relativo}): {modulo}")
            if modulo_bajo.split(".")[0] in self._PREFIJOS_EXTERNOS:
                errores.append(f"Import externo no permitido en dominio ({relativo}): {modulo}")

    def _regla_imports_aplicacion(self, relativo: Path, imports: set[str], errores: list[str]) -> None:
        for modulo in imports:
            if modulo.lower().startswith("presentacion"):
                errores.append(f"Import prohibido en aplicación ({relativo}): {modulo}")

    def _regla_imports_presentacion(self, relativo: Path, imports: set[str], errores: list[str]) -> None:
        for modulo in imports:
            if modulo.lower().startswith("infraestructura"):
                errores.append(f"Import prohibido en presentación ({relativo}): {modulo}")

    def _detectar_ciclos_basicos(self, grafo_imports: dict[str, set[str]]) -> list[str]:
        errores: list[str] = []
        for modulo, dependencias in grafo_imports.items():
            for dependencia in dependencias:
                if dependencia in grafo_imports and modulo in grafo_imports.get(dependencia, set()):
                    errores.append(f"Import circular detectado entre {modulo} y {dependencia}")
        return sorted(set(errores))

    def _ruta_a_modulo(self, relativa: Path) -> str:
        sin_sufijo = relativa.with_suffix("")
        return ".".join(sin_sufijo.parts)

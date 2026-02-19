"""Regla que evita imports desde dominio hacia presentación."""

from __future__ import annotations

from pathlib import Path
import re

from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_base import ReglaDependencia
from aplicacion.casos_uso.auditoria.validadores.validador_base import ContextoAuditoria, ResultadoValidacion


class ReglaDominioNoDependeDeOtrasCapas(ReglaDependencia):
    """Valida import prohibido de presentación dentro de dominio."""

    def __init__(self) -> None:
        self._patron_import = re.compile(r"^\s*import\s+([\w\.]+)", re.MULTILINE)
        self._patron_from = re.compile(r"^\s*from\s+([\w\.]+)\s+import\s+", re.MULTILINE)

    def evaluar(self, contexto: ContextoAuditoria) -> ResultadoValidacion:
        errores: list[str] = []
        for archivo in contexto.base.rglob("*.py"):
            relativo = self._obtener_relativo(contexto.base, archivo)
            if relativo is None or not relativo.parts or relativo.parts[0] != "dominio":
                continue
            imports = self._extraer_imports(archivo)
            for modulo in imports:
                if modulo.lower().startswith("presentacion"):
                    errores.append(f"Import prohibido en dominio ({relativo}): {modulo}")
        return ResultadoValidacion(exito=not errores, errores=errores)

    def _obtener_relativo(self, base: Path, archivo: Path) -> Path | None:
        try:
            return archivo.relative_to(base)
        except ValueError:
            return None

    def _extraer_imports(self, archivo: Path) -> set[str]:
        contenido = archivo.read_text(encoding="utf-8")
        return set(self._patron_import.findall(contenido)) | set(self._patron_from.findall(contenido))

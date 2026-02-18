"""Caso de uso para auditar requisitos mínimos de proyecto generado."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


@dataclass
class ResultadoAuditoria:
    """Resultado de auditoría mínima del proyecto generado."""

    valido: bool
    lista_errores: list[str] = field(default_factory=list)


class AuditarProyectoGenerado:
    """Verifica presencia de artefactos mínimos generados."""

    REQUERIDOS = [
        "manifest.json",
        "README.md",
        "VERSION",
        "logs",
        "scripts/lanzar_app.bat",
        "scripts/ejecutar_tests.bat",
    ]

    def ejecutar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        """Valida si el proyecto generado cumple los artefactos obligatorios."""
        base = Path(ruta_proyecto)
        errores: list[str] = []

        for relativo in self.REQUERIDOS:
            if not (base / relativo).exists():
                errores.append(f"No existe el recurso obligatorio: {relativo}")

        resultado = ResultadoAuditoria(valido=not errores, lista_errores=errores)
        LOGGER.info(
            "Resultado auditoría proyecto=%s valido=%s errores=%s",
            ruta_proyecto,
            resultado.valido,
            resultado.lista_errores,
        )
        return resultado

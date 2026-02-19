"""Paso para ejecutar auditoría posterior a la generación."""

from __future__ import annotations

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import (
    AuditarProyectoGenerado,
    ResultadoAuditoria,
)
from aplicacion.casos_uso.generacion.pasos.errores_pipeline import ErrorAuditoriaGeneracion


class EjecutorAuditoriaGeneracion:
    """Ejecuta la auditoría y devuelve su resultado."""

    def __init__(self, auditor: AuditarProyectoGenerado) -> None:
        self._auditor = auditor

    def ejecutar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        try:
            return self._auditor.auditar(ruta_proyecto)
        except (ValueError, OSError, RuntimeError) as exc:
            raise ErrorAuditoriaGeneracion("Falló la auditoría de la generación MVP.") from exc

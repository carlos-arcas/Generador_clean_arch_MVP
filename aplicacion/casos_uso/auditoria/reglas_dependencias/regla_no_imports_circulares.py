"""Regla opcional para detectar imports circulares."""

from __future__ import annotations

from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_base import ReglaDependencia
from aplicacion.casos_uso.auditoria.validadores.validador_base import ContextoAuditoria, ResultadoValidacion


class ReglaNoImportsCirculares(ReglaDependencia):
    """Implementación de marcador para futura validación de ciclos."""

    def evaluar(self, contexto: ContextoAuditoria) -> ResultadoValidacion:
        del contexto
        return ResultadoValidacion(exito=True, errores=[])

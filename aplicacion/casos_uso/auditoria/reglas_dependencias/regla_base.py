"""Contrato base para reglas de dependencias de capas."""

from __future__ import annotations

from abc import ABC, abstractmethod

from aplicacion.casos_uso.auditoria.validadores.validador_base import ContextoAuditoria, ResultadoValidacion


class ReglaDependencia(ABC):
    """Define la interfaz para validar reglas de dependencias entre capas."""

    @abstractmethod
    def evaluar(self, contexto: ContextoAuditoria) -> ResultadoValidacion:
        """Ejecuta la regla sobre el contexto de auditoría y devuelve su resultado."""

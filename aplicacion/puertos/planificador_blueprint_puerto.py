"""Puerto para obtener rutas generadas por blueprint en modo dry-run."""

from __future__ import annotations

from abc import ABC, abstractmethod

from dominio.especificacion import EspecificacionProyecto


class PlanificadorBlueprintPuerto(ABC):
    @abstractmethod
    def obtener_rutas_generadas(self, blueprint_id: str, especificacion: EspecificacionProyecto) -> set[str]:
        """Retorna rutas que un blueprint produciría sin escribir en disco."""

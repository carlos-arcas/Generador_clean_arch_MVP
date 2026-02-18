"""Puerto para generación del manifiesto del proyecto."""

from __future__ import annotations

from typing import Protocol

from dominio.modelos import EspecificacionProyecto


class GeneradorManifestPuerto(Protocol):
    """Contrato para construir el manifiesto de un proyecto generado."""

    def generar(
        self,
        ruta_proyecto: str,
        especificacion_proyecto: EspecificacionProyecto,
        blueprints: list[str],
        archivos_generados: list[str],
    ) -> None:
        """Genera y persiste el manifiesto del proyecto."""


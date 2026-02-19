"""DTO de entrada para auditoría de finalización E2E."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DtoAuditoriaFinalizacionEntrada:
    """Parámetros de entrada para ejecutar la auditoría completa."""

    ruta_preset: str
    ruta_salida_auditoria: str | None = None

    def resolver_ruta_sandbox(self, id_ejecucion: str, base_tmp: Path) -> Path:
        """Devuelve la ruta sandbox final para esta ejecución."""
        if self.ruta_salida_auditoria:
            return Path(self.ruta_salida_auditoria)
        return base_tmp / "auditoria" / id_ejecucion

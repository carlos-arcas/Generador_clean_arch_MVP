"""DTO de salida para auditoría de finalización E2E."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DtoEtapaAuditoria:
    nombre: str
    estado: str
    evidencia: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DtoAuditoriaFinalizacionSalida:
    id_ejecucion: str
    ruta_sandbox: str
    etapas: list[DtoEtapaAuditoria]
    reporte_markdown: str
    ruta_reporte: str

    @property
    def exito_global(self) -> bool:
        return all(etapa.estado != "FAIL" for etapa in self.etapas)

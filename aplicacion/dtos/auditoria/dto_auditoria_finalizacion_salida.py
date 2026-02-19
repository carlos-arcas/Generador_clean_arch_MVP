"""DTOs de salida para auditoría de finalización E2E."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ResultadoEtapa:
    """Resultado consolidado de una etapa del pipeline de auditoría."""

    nombre: str
    estado: str
    duracion_ms: int
    resumen: str
    tipo_fallo: str | None = None
    codigo: str | None = None
    mensaje_usuario: str | None = None
    detalle_tecnico: str | None = None


@dataclass(frozen=True)
class ConflictosFinalizacion:
    """Detalle de rutas duplicadas detectadas durante preflight."""

    total_rutas_duplicadas: int
    rutas_duplicadas: list[str]
    rutas_por_blueprint: dict[str, list[str]]


@dataclass(frozen=True)
class DtoAuditoriaFinalizacionSalida:
    """Salida completa del auditor E2E."""

    id_ejecucion: str
    ruta_sandbox: str
    etapas: list[ResultadoEtapa]
    conflictos: ConflictosFinalizacion | None
    evidencias: dict[str, str] = field(default_factory=dict)

    @property
    def exito_global(self) -> bool:
        return all(etapa.estado != "FAIL" for etapa in self.etapas)

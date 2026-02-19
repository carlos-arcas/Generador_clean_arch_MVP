"""DTO del informe de finalización E2E."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DtoEtapaInforme:
    nombre: str
    estado: str
    duracion_ms: int
    resumen: str
    evidencias_texto: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DtoConflictosRutasInforme:
    total: int = 0
    ejemplos_top: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DtoErrorTecnicoInforme:
    tipo: str
    mensaje: str
    origen: str
    linea_raise: str
    stacktrace_recortado: list[str]


@dataclass(frozen=True)
class DtoInformeFinalizacion:
    id_ejecucion: str
    fecha_iso: str
    preset_origen: str
    sandbox: str
    evidencias: str
    estado_global: str
    tipo_fallo_dominante: str
    codigo_fallo: str
    etapas: list[DtoEtapaInforme]
    conflictos_rutas: DtoConflictosRutasInforme = field(default_factory=DtoConflictosRutasInforme)
    warnings: list[str] = field(default_factory=list)
    error_tecnico: DtoErrorTecnicoInforme | None = None

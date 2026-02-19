"""DTO del informe de finalización E2E."""

from __future__ import annotations

from dataclasses import dataclass, field

from aplicacion.dtos.blueprints import DtoConflictoBlueprint


@dataclass(frozen=True)
class DtoEtapaInforme:
    nombre: str
    estado: str
    duracion_ms: int
    resumen: str
    evidencias_texto: list[str] = field(default_factory=list)
    tipo_fallo: str | None = None
    codigo: str | None = None
    mensaje_usuario: str | None = None


@dataclass(frozen=True)
class DtoConflictosRutasInforme:
    total: int = 0
    ejemplos_top: list[str] = field(default_factory=list)
    rutas_por_blueprint: dict[str, list[str]] = field(default_factory=dict)


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
    evidencias: EvidenciasCompat
    estado_global: str
    tipo_fallo_dominante: str
    codigo_fallo: str
    etapas: list[DtoEtapaInforme]
    conflictos_rutas: DtoConflictosRutasInforme = field(default_factory=DtoConflictosRutasInforme)
    conflictos_declarativos: list[DtoConflictoBlueprint] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error_tecnico: DtoErrorTecnicoInforme | None = None

    @property
    def ruta_sandbox(self) -> str:
        return self.sandbox

    @property
    def conflictos(self) -> DtoConflictosRutasInforme:
        return self.conflictos_rutas

    @property
    def exito_global(self) -> bool:
        return self.estado_global == "PASS"
class EvidenciasCompat(str):
    def __new__(cls, ruta: str, detalle: dict[str, str] | None = None):
        instancia = super().__new__(cls, ruta)
        instancia._detalle = detalle or {}
        return instancia

    def __getitem__(self, item: str) -> str:
        return self._detalle[item]

    def get(self, clave: str, por_defecto: str | None = None) -> str | None:
        return self._detalle.get(clave, por_defecto)

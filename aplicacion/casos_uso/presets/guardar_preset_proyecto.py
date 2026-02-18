"""Caso de uso para guardar presets de proyecto."""

from __future__ import annotations

from aplicacion.casos_uso.construir_especificacion_proyecto import ConstruirEspecificacionProyecto
from aplicacion.dtos.proyecto import DtoProyectoEntrada
from aplicacion.errores import ErrorValidacion
from aplicacion.puertos.almacen_presets import AlmacenPresets
from dominio.preset.preset_proyecto import PresetProyecto


class GuardarPresetProyecto:
    """Valida y delega guardado de preset en infraestructura."""

    def __init__(self, almacen: AlmacenPresets) -> None:
        self._almacen = almacen
        self._constructor = ConstruirEspecificacionProyecto()

    def ejecutar(self, preset: PresetProyecto, ruta_destino: str | None = None) -> str:
        try:
            preset.validar()
        except ValueError as exc:
            raise ErrorValidacion(str(exc)) from exc
        return self._almacen.guardar(preset, ruta_destino)

    def ejecutar_desde_dto(
        self,
        *,
        nombre: str,
        proyecto: DtoProyectoEntrada,
        blueprints: list[str],
        metadata: dict[str, object],
        ruta_destino: str | None = None,
    ) -> str:
        preset = PresetProyecto(
            nombre=nombre,
            especificacion=self._constructor.ejecutar(proyecto),
            blueprints=blueprints,
            metadata=metadata,
        )
        return self.ejecutar(preset, ruta_destino)

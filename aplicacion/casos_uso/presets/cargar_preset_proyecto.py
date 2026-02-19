"""Caso de uso para cargar presets de proyecto."""

from __future__ import annotations

from aplicacion.errores import ErrorValidacion
from aplicacion.puertos.almacen_presets import AlmacenPresets


class CargarPresetProyecto:
    """Carga presets por nombre y normaliza errores de validación."""

    def __init__(self, almacen: AlmacenPresets) -> None:
        self._almacen = almacen

    def ejecutar(self, nombre_preset: str):
        try:
            return self._almacen.cargar(nombre_preset)
        except (ValueError, TypeError, KeyError) as exc:
            raise ErrorValidacion(f"Preset inválido: {exc}") from exc

    def listar_presets(self) -> list[str]:
        """Expone la lista de presets sin revelar detalles internos del almacén."""
        return list(self._almacen.listar())

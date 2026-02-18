"""Casos de uso para presets de proyecto."""

from .cargar_preset_proyecto import CargarPresetProyecto
from .guardar_preset_proyecto import GuardarPresetProyecto


class GuardarPreset(GuardarPresetProyecto):
    """Alias retrocompatible para firmas anteriores."""

    def ejecutar(self, preset, incluir_ruta_destino: bool = False):  # type: ignore[override]
        return super().ejecutar(preset)


class CargarPreset(CargarPresetProyecto):
    """Alias retrocompatible para firmas anteriores."""

    def ejecutar(self, ruta: str, ruta_destino_forzada: str | None = None):  # type: ignore[override]
        preset = super().ejecutar(ruta)
        if ruta_destino_forzada is not None:
            preset.especificacion.ruta_destino = ruta_destino_forzada
        return preset


__all__ = [
    "GuardarPresetProyecto",
    "CargarPresetProyecto",
    "GuardarPreset",
    "CargarPreset",
]

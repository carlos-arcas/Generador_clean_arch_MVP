"""Compatibilidad: alias del repositorio JSON de presets en disco."""

from infraestructura.presets.repositorio_presets_json import RepositorioPresetsJson


class AlmacenPresetsDisco(RepositorioPresetsJson):
    """Alias retrocompatible para el repositorio de presets JSON."""

"""Errores semánticos del dominio de generación de proyectos."""

from __future__ import annotations

from .errores_validacion import ErrorAplicacion


class ErrorGeneracionProyecto(ErrorAplicacion):
    """Error funcional al orquestar la generación de un proyecto."""


class ErrorConflictoArchivos(ErrorAplicacion):
    """Error por conflictos de rutas o estado de archivos."""


class ErrorBlueprintNoEncontrado(ErrorAplicacion):
    """Error cuando no existe el blueprint solicitado."""


class ErrorInfraestructura(ErrorAplicacion):
    """Error técnico proveniente de un adaptador de infraestructura."""

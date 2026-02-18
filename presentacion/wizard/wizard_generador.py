"""Módulo de compatibilidad del wizard de generación."""

from __future__ import annotations

from presentacion.trabajadores.trabajador_generacion import TrabajadorGeneracionMvp
from presentacion.wizard.wizard_principal import (
    BLUEPRINTS_MVP,
    ControladorWizardProyecto,
    WizardGeneradorProyectos,
)

__all__ = [
    "BLUEPRINTS_MVP",
    "ControladorWizardProyecto",
    "TrabajadorGeneracionMvp",
    "WizardGeneradorProyectos",
]

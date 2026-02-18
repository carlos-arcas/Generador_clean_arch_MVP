"""Compatibilidad de imports para wizard generador."""

from presentacion.wizard.controlador.controlador_wizard import ControladorWizardProyecto
from presentacion.wizard.wizard_principal import BLUEPRINTS_MVP, WizardGeneradorProyectos

__all__ = ["BLUEPRINTS_MVP", "ControladorWizardProyecto", "WizardGeneradorProyectos"]

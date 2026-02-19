"""Micro-framework interno para validaciones reutilizables."""

from .motor_validacion import MotorValidacion
from .regla_validacion import ReglaValidacion
from .resultado_validacion import ResultadoValidacion

__all__ = ["ReglaValidacion", "ResultadoValidacion", "MotorValidacion"]


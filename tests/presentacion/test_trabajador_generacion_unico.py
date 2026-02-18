"""Pruebas para validar unificación del trabajador de generación."""

from __future__ import annotations

import importlib

import pytest

pytest.importorskip("PySide6.QtCore", exc_type=ImportError)
pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from presentacion.trabajadores import trabajador_generacion
from presentacion.trabajadores.trabajador_generacion import TrabajadorGeneracionMvp
from presentacion.wizard import wizard_generador


def test_solo_hay_un_trabajador_publico_importable() -> None:
    assert hasattr(trabajador_generacion, "TrabajadorGeneracionMvp")
    assert not hasattr(trabajador_generacion, "TrabajadorGeneracion")

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("presentacion.wizard.trabajadores.trabajador_generacion")


def test_wizard_oficial_usa_trabajador_canonico() -> None:
    assert wizard_generador.TrabajadorGeneracionMvp is TrabajadorGeneracionMvp

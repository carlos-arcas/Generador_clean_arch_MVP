"""Pruebas de inicialización del wizard principal."""

from __future__ import annotations

import inspect
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication

from infraestructura.bootstrap import construir_contenedor_aplicacion
from presentacion.wizard.wizard_generador import WizardGeneradorProyectos


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def _crear_wizard() -> WizardGeneradorProyectos:
    contenedor = construir_contenedor_aplicacion()
    return WizardGeneradorProyectos(
        generar_proyecto=contenedor.generar_proyecto_mvp,
        guardar_preset=contenedor.guardar_preset_proyecto,
        cargar_preset=contenedor.cargar_preset_proyecto,
        guardar_credencial=contenedor.guardar_credencial,
        catalogo_blueprints=contenedor.catalogo_blueprints,
    )


def test_wizard_instancia_sin_error() -> None:
    _app()

    wizard = _crear_wizard()

    assert wizard is not None


def test_componentes_clave_inicializados() -> None:
    _app()

    wizard = _crear_wizard()

    assert wizard.pagina_datos is not None
    assert wizard.pagina_clases is not None
    assert wizard.pagina_persistencia is not None
    assert wizard.pagina_resumen is not None
    assert wizard._etiqueta_estado is not None
    assert wizard._barra_progreso is not None


def test_init_tiene_tamano_reducido() -> None:
    codigo_init = inspect.getsource(WizardGeneradorProyectos.__init__)
    lineas = [linea for linea in codigo_init.splitlines() if linea.strip()]

    assert len(lineas) < 50


def test_wiring_minimo_de_senales() -> None:
    codigo_wiring = inspect.getsource(WizardGeneradorProyectos._conectar_senales)

    assert "_guardar_preset_desde_ui" in codigo_wiring
    assert "_cargar_preset_desde_ui" in codigo_wiring
    assert "_al_finalizar" in codigo_wiring

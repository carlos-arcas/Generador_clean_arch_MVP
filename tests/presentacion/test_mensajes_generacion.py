"""Pruebas de mensajes humanos al terminar la generación."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication

from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvpSalida
from presentacion.wizard.wizard_generador import WizardGeneradorProyectos


@pytest.fixture
def app_qt() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def test_mensaje_exito_muestra_resumen_generacion(
    app_qt: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wizard = WizardGeneradorProyectos()

    capturado: dict[str, str] = {}

    def _fake_dialogo(salida: GenerarProyectoMvpSalida) -> None:
        capturado["ruta"] = salida.ruta_generada
        capturado["archivos"] = str(salida.archivos_generados)
        capturado["errores"] = str(len(salida.errores))
        capturado["warnings"] = str(len(salida.warnings))

    monkeypatch.setattr(wizard, "_mostrar_dialogo_exito", _fake_dialogo)

    wizard._on_generacion_exitosa(
        GenerarProyectoMvpSalida(
            ruta_generada="/tmp/demo",
            archivos_generados=12,
            valido=True,
            errores=["e1"],
            warnings=["w1", "w2"],
        )
    )

    assert capturado == {
        "ruta": "/tmp/demo",
        "archivos": "12",
        "errores": "1",
        "warnings": "2",
    }


def test_mensaje_error_invoca_dialogo_logs(
    app_qt: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wizard = WizardGeneradorProyectos()

    llamado = {"error": False}
    monkeypatch.setattr(wizard, "_mostrar_error_generacion", lambda: llamado.__setitem__("error", True))

    wizard._on_generacion_error("fallo", "stack interno")

    assert llamado["error"] is True

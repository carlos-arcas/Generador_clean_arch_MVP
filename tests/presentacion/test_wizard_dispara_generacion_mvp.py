"""Pruebas de wiring para disparo de generación MVP desde wizard."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication
QMessageBox = QtWidgets.QMessageBox

from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvpSalida
from presentacion.wizard.wizard_generador import WizardGeneradorProyectos


class GeneradorMvpDoble:
    def __init__(self) -> None:
        self.entradas = []

    def ejecutar(self, entrada):  # noqa: ANN001
        self.entradas.append(entrada)
        return GenerarProyectoMvpSalida(
            ruta_generada=entrada.ruta_destino,
            archivos_generados=5,
            valido=True,
            errores=[],
            warnings=[],
        )


@pytest.fixture
def app_qt() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def test_wizard_finalizar_dispara_caso_uso_y_bloquea_botones(
    app_qt: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generador_doble = GeneradorMvpDoble()
    wizard = WizardGeneradorProyectos(generador_mvp=generador_doble)
    wizard.pagina_datos.campo_nombre.setText("MiProyecto")
    wizard.pagina_datos.campo_ruta.setText("/tmp/mi_proyecto")
    wizard.pagina_clases.anadir_clase("Cliente")
    wizard.pagina_clases.anadir_atributo(nombre_atributo="id", tipo="int", obligatorio=True)
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.Ok)

    estados_durante_start: list[tuple[bool, bool, bool]] = []

    def _start_inmediato(worker):  # noqa: ANN001
        estados_durante_start.append(
            (
                wizard.button(wizard.BackButton).isEnabled(),
                wizard.button(wizard.NextButton).isEnabled(),
                wizard.button(wizard.FinishButton).isEnabled(),
            )
        )
        worker.run()

    monkeypatch.setattr(wizard._pool, "start", _start_inmediato)

    wizard._al_finalizar()

    assert len(generador_doble.entradas) == 1
    assert generador_doble.entradas[0].blueprints == ["base_clean_arch", "crud_json"]
    assert estados_durante_start == [(False, False, False)]
    assert wizard.button(wizard.BackButton).isEnabled() is True
    assert wizard.button(wizard.NextButton).isEnabled() is True
    assert wizard.button(wizard.FinishButton).isEnabled() is True

"""Pruebas de cancelación segura del flujo de generación en background."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import (
    GenerarProyectoMvp,
    GenerarProyectoMvpEntrada,
)
from dominio.modelos import EspecificacionProyecto
from presentacion.wizard.wizard_generador import WizardGeneradorProyectos
from presentacion.wizard.trabajadores.trabajador_generacion import TrabajadorGeneracionMvp


class CrearPlanDoble:
    def ejecutar(self, _especificacion, _blueprints):  # noqa: ANN001
        return []


class EjecutarPlanDoble:
    def ejecutar(self, **_kwargs):  # noqa: ANN003
        return []


class SistemaArchivosDoble:
    def asegurar_directorio(self, ruta: str) -> None:
        Path(ruta).mkdir(parents=True, exist_ok=True)


class GeneradorManifestDoble:
    def generar(self, **_kwargs):  # noqa: ANN003
        return None


class AuditorDoble:
    def auditar(self, _ruta: str) -> ResultadoAuditoria:
        return ResultadoAuditoria()


@pytest.fixture
def app_qt() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def _crear_generador() -> GenerarProyectoMvp:
    return GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanDoble(),
        ejecutar_plan=EjecutarPlanDoble(),
        sistema_archivos=SistemaArchivosDoble(),
        generador_manifest=GeneradorManifestDoble(),
        auditor=AuditorDoble(),
    )


def test_cancelacion_elimina_carpeta_parcial(tmp_path: Path) -> None:
    entrada = GenerarProyectoMvpEntrada(
        especificacion_proyecto=EspecificacionProyecto(nombre_proyecto="demo", ruta_destino=str(tmp_path)),
        ruta_destino=str(tmp_path),
        nombre_proyecto="demo",
        blueprints=["base_clean_arch"],
    )
    worker = TrabajadorGeneracionMvp(caso_uso=_crear_generador(), entrada=entrada)
    worker.cancelar()

    mensajes_cancelacion: list[str] = []
    worker.senales.cancelado.connect(mensajes_cancelacion.append)

    worker.run()

    assert mensajes_cancelacion == ["Generación cancelada por el usuario."]
    assert not (tmp_path / "demo").exists()


def test_cancelacion_no_rompe_estado_wizard(app_qt: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    wizard = WizardGeneradorProyectos(generador_mvp=_crear_generador())
    wizard.pagina_datos.campo_nombre.setText("demo")
    wizard.pagina_datos.campo_ruta.setText("/tmp")

    monkeypatch.setattr(
        wizard,
        "_on_generacion_cancelada",
        lambda _mensaje: wizard._cambiar_estado_generando(False, "cancelado"),
    )

    def _start_cancelando(worker):  # noqa: ANN001
        worker.cancelar()
        worker.run()

    monkeypatch.setattr(wizard._pool, "start", _start_cancelando)

    wizard._al_finalizar()

    assert wizard.button(wizard.BackButton).isEnabled() is True
    assert wizard.button(wizard.NextButton).isEnabled() is True
    assert wizard.button(wizard.FinishButton).isEnabled() is True
    assert wizard._boton_cancelar_generacion.isVisible() is False

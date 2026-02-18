"""Pruebas mínimas de wiring para capa de presentación PySide6."""

from __future__ import annotations

import os
import pytest
from unittest.mock import Mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = QtWidgets.QApplication

from aplicacion.casos_uso.auditar_proyecto_generado import ResultadoAuditoria
from dominio.modelos import EspecificacionProyecto
from presentacion.trabajadores.trabajador_generacion import ResultadoGeneracion, TrabajadorGeneracion
from presentacion.ventana_principal import VentanaPrincipal
from presentacion.wizard_proyecto import PaginaBlueprints



def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def test_instanciar_ventana_principal() -> None:
    _app()
    ventana = VentanaPrincipal(version_generador="0.7.0")

    assert ventana.windowTitle() == "Generador Base Proyectos"
    assert ventana.wizard is not None


def test_trabajador_generacion_invoca_casos_de_uso() -> None:
    especificacion = EspecificacionProyecto(
        nombre_proyecto="demo",
        ruta_destino="salida/demo",
        descripcion="demo",
        version="0.7.0",
    )
    mock_plan = object()

    crear_plan = Mock()
    crear_plan.ejecutar.return_value = mock_plan

    ejecutar_plan = Mock()
    crear_plan_patch = Mock()
    actualizar_manifest_patch = Mock()

    resultado_auditoria = ResultadoAuditoria(valido=True, lista_errores=[])
    auditor = Mock()
    auditor.ejecutar.return_value = resultado_auditoria

    worker = TrabajadorGeneracion(
        especificacion=especificacion,
        blueprints=["base_clean_arch", "crud_json"],
        crear_plan_desde_blueprints=crear_plan,
        crear_plan_patch_desde_blueprints=crear_plan_patch,
        ejecutar_plan=ejecutar_plan,
        actualizar_manifest_patch=actualizar_manifest_patch,
        auditor=auditor,
        version_generador="0.7.0",
    )

    eventos_finalizados: list[ResultadoGeneracion] = []
    worker.senales.finalizado.connect(eventos_finalizados.append)

    worker.run()

    crear_plan.ejecutar.assert_called_once_with(especificacion, ["base_clean_arch", "crud_json"])
    crear_plan_patch.ejecutar.assert_not_called()
    ejecutar_plan.ejecutar.assert_called_once()
    actualizar_manifest_patch.ejecutar.assert_not_called()
    auditor.ejecutar.assert_called_once_with(
        "salida/demo",
        blueprints_usados=["base_clean_arch", "crud_json"],
    )
    assert eventos_finalizados
    assert eventos_finalizados[0].auditoria.valido is True


def test_pagina_blueprints_persistencia_exclusiva() -> None:
    _app()
    pagina = PaginaBlueprints()

    assert pagina.blueprints_seleccionados() == ["base_clean_arch", "crud_json"]

    pagina.persistencia_sqlite.setChecked(True)

    assert pagina.blueprints_seleccionados() == ["base_clean_arch", "crud_sqlite"]
    assert pagina.persistencia_json.isChecked() is False

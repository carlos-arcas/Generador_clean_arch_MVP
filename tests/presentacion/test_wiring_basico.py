"""Pruebas mínimas de wiring para capa de presentación PySide6."""

from __future__ import annotations

import os
from unittest.mock import Mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from aplicacion.casos_uso.auditar_proyecto_generado import ResultadoAuditoria
from dominio.modelos import EspecificacionProyecto
from presentacion.trabajadores.trabajador_generacion import ResultadoGeneracion, TrabajadorGeneracion
from presentacion.ventana_principal import VentanaPrincipal



def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    return app


def test_instanciar_ventana_principal() -> None:
    _app()
    ventana = VentanaPrincipal(version_generador="0.5.0")

    assert ventana.windowTitle() == "Generador Base Proyectos"
    assert ventana.wizard is not None


def test_trabajador_generacion_invoca_casos_de_uso() -> None:
    especificacion = EspecificacionProyecto(
        nombre_proyecto="demo",
        ruta_destino="salida/demo",
        descripcion="demo",
        version="0.5.0",
    )
    mock_plan = object()

    crear_plan = Mock()
    crear_plan.ejecutar.return_value = mock_plan

    ejecutar_plan = Mock()

    resultado_auditoria = ResultadoAuditoria(valido=True, lista_errores=[])
    auditor = Mock()
    auditor.ejecutar.return_value = resultado_auditoria

    worker = TrabajadorGeneracion(
        especificacion=especificacion,
        blueprints=["base_clean_arch", "crud_json"],
        crear_plan_desde_blueprints=crear_plan,
        ejecutar_plan=ejecutar_plan,
        auditor=auditor,
        version_generador="0.5.0",
    )

    eventos_finalizados: list[ResultadoGeneracion] = []
    worker.senales.finalizado.connect(eventos_finalizados.append)

    worker.run()

    crear_plan.ejecutar.assert_called_once_with(especificacion, ["base_clean_arch", "crud_json"])
    ejecutar_plan.ejecutar.assert_called_once()
    auditor.ejecutar.assert_called_once_with("salida/demo")
    assert eventos_finalizados
    assert eventos_finalizados[0].auditoria.valido is True

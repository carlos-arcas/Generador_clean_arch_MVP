"""Pruebas de integración mínima del composition root de infraestructura."""

from __future__ import annotations

from infraestructura.bootstrap import ContenedorAplicacion, construir_contenedor_aplicacion


def test_bootstrap_construye_contenedor_valido() -> None:
    contenedor = construir_contenedor_aplicacion()

    assert isinstance(contenedor, ContenedorAplicacion)
    assert contenedor.crear_plan_desde_blueprints is not None
    assert contenedor.generar_proyecto_mvp is not None
    assert contenedor.auditar_proyecto_generado is not None


def test_bootstrap_expone_casos_de_uso_invocables() -> None:
    contenedor = construir_contenedor_aplicacion()

    assert callable(contenedor.crear_plan_desde_blueprints.ejecutar)
    assert callable(contenedor.generar_proyecto_mvp.ejecutar)
    assert callable(contenedor.auditar_proyecto_generado.ejecutar)

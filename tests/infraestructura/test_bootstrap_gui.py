from __future__ import annotations

from infraestructura.bootstrap.bootstrap_gui import ContenedorGui, construir_contenedor_gui


def test_construir_contenedor_gui_devuelve_objeto_valido() -> None:
    contenedor = construir_contenedor_gui()

    assert isinstance(contenedor, ContenedorGui)


def test_contenedor_gui_expone_casos_de_uso_principales() -> None:
    contenedor = construir_contenedor_gui()

    assert contenedor.generar_proyecto_mvp is not None
    assert contenedor.guardar_preset_proyecto is not None
    assert contenedor.consultar_catalogo_blueprints is not None


def test_catalogo_blueprints_se_consulta_desde_caso_de_uso() -> None:
    contenedor = construir_contenedor_gui()

    catalogo = contenedor.consultar_catalogo_blueprints.ejecutar()

    assert isinstance(catalogo, list)

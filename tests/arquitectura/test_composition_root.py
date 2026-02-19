from __future__ import annotations

from pathlib import Path

from infraestructura.bootstrap import construir_contenedor_aplicacion


def test_construir_contenedor_aplicacion_expone_casos_de_uso_principales() -> None:
    contenedor = construir_contenedor_aplicacion()

    assert contenedor.generar_proyecto_mvp is not None
    assert contenedor.auditar_proyecto_generado is not None
    assert contenedor.crear_plan_desde_blueprints is not None
    assert contenedor.crear_plan_patch_desde_blueprints is not None
    assert contenedor.ejecutar_plan is not None
    assert contenedor.actualizar_manifest_patch is not None
    assert contenedor.guardar_preset_proyecto is not None
    assert contenedor.cargar_preset_proyecto is not None
    assert contenedor.guardar_credencial is not None


def test_cli_importa_bootstrap_por_contexto() -> None:
    contenido = Path("presentacion/cli/__main__.py").read_text(encoding="utf-8")

    assert "from infraestructura.bootstrap.bootstrap_cli import construir_contenedor_cli" in contenido


def test_wizard_no_importa_infraestructura_directamente() -> None:
    contenido = Path("presentacion/wizard/wizard_generador.py").read_text(encoding="utf-8")

    assert "from infraestructura." not in contenido
    assert "import infraestructura" not in contenido

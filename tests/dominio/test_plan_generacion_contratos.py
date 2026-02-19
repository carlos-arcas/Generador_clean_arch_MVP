from __future__ import annotations

from dominio.plan_generacion import ArchivoGenerado, PlanGeneracion


def test_plan_generacion_conserva_invariantes_basicos() -> None:
    archivo = ArchivoGenerado(ruta_relativa="README.md", contenido_texto="# demo")
    plan = PlanGeneracion(archivos=[archivo])

    assert plan.archivos
    assert plan.archivos[0].ruta_relativa == "README.md"
    assert isinstance(plan.obtener_rutas(), list)
    assert plan.obtener_rutas() == ["README.md"]


def test_plan_generacion_fusiona_y_mantiene_todas_las_rutas() -> None:
    plan_a = PlanGeneracion([ArchivoGenerado("a.txt", "A")])
    plan_b = PlanGeneracion([ArchivoGenerado("b.txt", "B")])

    fusion = plan_a.fusionar(plan_b)

    assert fusion.obtener_rutas() == ["a.txt", "b.txt"]

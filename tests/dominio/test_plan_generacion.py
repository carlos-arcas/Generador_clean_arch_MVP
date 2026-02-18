import pytest

from dominio.modelos import ArchivoGenerado, ErrorValidacionDominio, PlanGeneracion


def test_obtener_rutas_retorna_todas_las_rutas() -> None:
    plan = PlanGeneracion(
        archivos=[
            ArchivoGenerado("README.md", "a"),
            ArchivoGenerado("VERSION", "1.0.0"),
        ]
    )

    assert plan.obtener_rutas() == ["README.md", "VERSION"]


def test_comprobar_duplicados_detecta_repetidos() -> None:
    plan = PlanGeneracion(
        archivos=[
            ArchivoGenerado("README.md", "a"),
            ArchivoGenerado("README.md", "b"),
        ]
    )

    with pytest.raises(ErrorValidacionDominio, match="duplicadas"):
        plan.comprobar_duplicados()


def test_comprobar_duplicados_permte_plan_unico() -> None:
    plan = PlanGeneracion(
        archivos=[
            ArchivoGenerado("README.md", "a"),
            ArchivoGenerado("docs/guia.md", "b"),
        ]
    )

    plan.comprobar_duplicados()

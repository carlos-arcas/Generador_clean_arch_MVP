import pytest

from dominio.modelos import ArchivoGenerado, ErrorValidacionDominio, PlanGeneracion


def test_agregar_archivo_y_fusionar_planes() -> None:
    plan_base = PlanGeneracion()
    plan_base.agregar_archivo(ArchivoGenerado("README.md", "ok"))
    plan_extra = PlanGeneracion([ArchivoGenerado("VERSION", "1.0.0")])

    combinado = plan_base.fusionar(plan_extra)

    assert combinado.obtener_rutas() == ["README.md", "VERSION"]


def test_validar_sin_conflictos_falla_con_ruta_duplicada() -> None:
    plan_a = PlanGeneracion([ArchivoGenerado("README.md", "a")])
    plan_b = PlanGeneracion([ArchivoGenerado("README.md", "b")])

    with pytest.raises(ErrorValidacionDominio, match="duplicadas"):
        plan_a.fusionar(plan_b)

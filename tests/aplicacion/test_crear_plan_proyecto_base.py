from aplicacion.casos_uso.crear_plan_proyecto_base import CrearPlanProyectoBase
from dominio.modelos import EspecificacionProyecto


def test_crear_plan_proyecto_base_genera_archivos_minimos() -> None:
    especificacion = EspecificacionProyecto(
        nombre_proyecto="demo",
        ruta_destino="/tmp/demo",
        descripcion="descripcion",
        version="0.3.1",
    )

    plan = CrearPlanProyectoBase().ejecutar(especificacion)
    rutas = plan.obtener_rutas()

    assert "README.md" in rutas
    assert "VERSION" in rutas
    assert "CHANGELOG.md" in rutas
    contenido_version = [a for a in plan.archivos if a.ruta_relativa == "VERSION"][0]
    assert contenido_version.contenido_texto == "0.3.1"

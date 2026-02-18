from dominio.modelos import EspecificacionProyecto
from dominio.preset.preset_proyecto import PresetProyecto
from infraestructura.almacen_presets_disco import AlmacenPresetsDisco


def test_almacen_presets_disco_guarda_y_carga(tmp_path) -> None:
    almacen = AlmacenPresetsDisco(str(tmp_path / "presets"))
    preset = PresetProyecto(
        nombre="demo",
        especificacion=EspecificacionProyecto(nombre_proyecto="x", ruta_destino="/tmp/x"),
        blueprints=["base_clean_arch_v1"],
        metadata={"persistencia": "JSON"},
    )

    ruta = almacen.guardar(preset)
    cargado = almacen.cargar("demo")

    assert (tmp_path / "presets" / "demo.json").exists()
    assert ruta.endswith("demo.json")
    assert cargado.nombre == "demo"

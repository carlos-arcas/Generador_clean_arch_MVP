from aplicacion.casos_uso.presets import CargarPresetProyecto, GuardarPresetProyecto
from dominio.modelos import EspecificacionClase, EspecificacionProyecto
from dominio.preset.preset_proyecto import PresetProyecto
from infraestructura.presets.repositorio_presets_json import RepositorioPresetsJson


def test_guardar_y_cargar_preset(tmp_path) -> None:
    repositorio = RepositorioPresetsJson(str(tmp_path / "presets"))
    preset = PresetProyecto(
        nombre="demo",
        especificacion=EspecificacionProyecto(
            nombre_proyecto="demo",
            ruta_destino="/tmp/demo",
            version="1.0.0",
            clases=[EspecificacionClase(nombre="Cliente")],
        ),
        blueprints=["base_clean_arch_v1", "crud_json_v1"],
        metadata={"persistencia": "JSON"},
    )

    GuardarPresetProyecto(repositorio).ejecutar(preset)
    cargado = CargarPresetProyecto(repositorio).ejecutar("demo")

    assert cargado.nombre == "demo"
    assert cargado.especificacion.nombre_proyecto == "demo"
    assert cargado.blueprints == ["base_clean_arch_v1", "crud_json_v1"]

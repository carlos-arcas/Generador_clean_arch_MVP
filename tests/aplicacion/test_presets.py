import pytest

from aplicacion.casos_uso.presets import CargarPresetProyecto, GuardarPresetProyecto
from aplicacion.errores import ErrorValidacion
from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto
from dominio.preset.preset_proyecto import PresetProyecto
from infraestructura.presets.repositorio_presets_json import RepositorioPresetsJson


def _preset_demo(nombre: str = "demo") -> PresetProyecto:
    return PresetProyecto(
        nombre=nombre,
        especificacion=EspecificacionProyecto(
            nombre_proyecto="Demo",
            ruta_destino="/tmp/demo",
            descripcion="Proyecto demo",
            version="1.0.0",
            clases=[
                EspecificacionClase(
                    nombre="Cliente",
                    atributos=[EspecificacionAtributo(nombre="email", tipo="str", obligatorio=True)],
                )
            ],
        ),
        blueprints=["base_clean_arch_v1", "crud_json_v1"],
        metadata={"persistencia": "JSON"},
    )


def test_guardar_preset_crea_archivo(tmp_path) -> None:
    repositorio = RepositorioPresetsJson(str(tmp_path / "presets"))

    ruta = GuardarPresetProyecto(repositorio).ejecutar(_preset_demo())

    assert (tmp_path / "presets" / "demo.json").exists()
    assert ruta.endswith("demo.json")


def test_cargar_preset_reconstruye_estructura(tmp_path) -> None:
    repositorio = RepositorioPresetsJson(str(tmp_path / "presets"))
    GuardarPresetProyecto(repositorio).ejecutar(_preset_demo())

    cargado = CargarPresetProyecto(repositorio).ejecutar("demo")

    assert cargado.nombre == "demo"
    assert cargado.especificacion.nombre_proyecto == "Demo"
    assert cargado.especificacion.clases[0].atributos[0].nombre == "email"
    assert cargado.blueprints == ["base_clean_arch_v1", "crud_json_v1"]


def test_listar_presets_retorna_nombres(tmp_path) -> None:
    repositorio = RepositorioPresetsJson(str(tmp_path / "presets"))
    GuardarPresetProyecto(repositorio).ejecutar(_preset_demo("demo"))
    GuardarPresetProyecto(repositorio).ejecutar(_preset_demo("demo2"))

    assert repositorio.listar() == ["demo", "demo2"]


def test_cargar_json_corrupto_lanza_excepcion_controlada(tmp_path) -> None:
    carpeta = tmp_path / "presets"
    carpeta.mkdir(parents=True)
    (carpeta / "roto.json").write_text("{ invalido", encoding="utf-8")

    with pytest.raises(ValueError, match="JSON inválido"):
        RepositorioPresetsJson(str(carpeta)).cargar("roto")


def test_cargar_json_estructura_invalida_lanza_error_validacion(tmp_path) -> None:
    carpeta = tmp_path / "presets"
    carpeta.mkdir(parents=True)
    (carpeta / "roto.json").write_text('{"nombre": "roto"}', encoding="utf-8")

    with pytest.raises(ErrorValidacion, match="Preset inválido"):
        CargarPresetProyecto(RepositorioPresetsJson(str(carpeta))).ejecutar("roto")

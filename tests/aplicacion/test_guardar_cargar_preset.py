import pytest

from aplicacion.casos_uso.presets import CargarPreset, GuardarPreset
from aplicacion.errores import ErrorValidacion
from aplicacion.puertos.almacen_presets import AlmacenPresets
from dominio.modelos import EspecificacionClase, EspecificacionProyecto, PresetProyecto


class AlmacenEnMemoria(AlmacenPresets):
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    def guardar(self, nombre: str, contenido_json: dict) -> str:
        ruta = f"mem://{nombre}.json"
        self._store[ruta] = contenido_json
        return ruta

    def cargar(self, ruta: str) -> dict:
        return self._store[ruta]


def _preset_demo() -> PresetProyecto:
    return PresetProyecto(
        nombre_preset="demo",
        especificacion=EspecificacionProyecto(
            nombre_proyecto="demo",
            ruta_destino="/tmp/demo",
            version="1.0.0",
            clases=[EspecificacionClase(nombre="Cliente")],
        ),
        blueprints=["base_clean_arch", "crud_json", "export_csv"],
        opciones={"patch": False},
    )


def test_guardar_y_cargar_preset() -> None:
    almacen = AlmacenEnMemoria()
    ruta = GuardarPreset(almacen).ejecutar(_preset_demo())

    preset = CargarPreset(almacen).ejecutar(ruta, ruta_destino_forzada="/tmp/otro")

    assert preset.nombre_preset == "demo"
    assert preset.especificacion.nombre_proyecto == "demo"
    assert preset.especificacion.ruta_destino == "/tmp/otro"
    assert preset.blueprints == ["base_clean_arch", "crud_json", "export_csv"]


def test_cargar_preset_invalido_devuelve_error_validacion() -> None:
    almacen = AlmacenEnMemoria()
    almacen.guardar("roto", {"nombre_preset": "roto"})

    with pytest.raises(ErrorValidacion, match="Preset inválido"):
        CargarPreset(almacen).ejecutar("mem://roto.json")

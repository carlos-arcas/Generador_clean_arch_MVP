from pathlib import Path
import re

from aplicacion.casos_uso.presets.cargar_preset_proyecto import CargarPresetProyecto


class _AlmacenPresetsStub:
    def __init__(self, nombres: list[str]) -> None:
        self._nombres = nombres

    def cargar(self, nombre_preset: str):  # pragma: no cover - no aplica en este test
        raise NotImplementedError

    def listar(self) -> list[str]:
        return self._nombres


def test_wizard_no_accede_a_almacen_privado() -> None:
    ruta_wizard = Path("presentacion/wizard/wizard_generador.py")
    contenido = ruta_wizard.read_text(encoding="utf-8")

    assert "._almacen" not in contenido


def test_listar_presets_delega_sin_exponer_estado_mutable() -> None:
    origen = ["demo", "demo2"]
    servicio = CargarPresetProyecto(_AlmacenPresetsStub(origen))

    listados = servicio.listar_presets()
    assert listados == ["demo", "demo2"]

    listados.append("nuevo")
    assert servicio.listar_presets() == ["demo", "demo2"]


def test_presentacion_no_tiene_acceso_encadenado_a_privados() -> None:
    patron = re.compile(r"\._[a-zA-Z0-9]+\._[a-zA-Z0-9]+")

    for archivo in Path("presentacion").rglob("*.py"):
        contenido = archivo.read_text(encoding="utf-8")
        assert patron.search(contenido) is None, f"Acceso privado detectado en {archivo.as_posix()}"

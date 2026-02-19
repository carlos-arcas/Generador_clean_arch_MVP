from __future__ import annotations

from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from aplicacion.errores import ErrorValidacion
from dominio.especificacion import EspecificacionProyecto
from dominio.preset.preset_proyecto import PresetProyecto
from presentacion.cli.comandos.comando_generar import ejecutar_comando_generar
import presentacion.cli.__main__ as cli_main


@dataclass
class _CasoUsoStub:
    retorno: object

    def __post_init__(self) -> None:
        self.llamadas: list[tuple[tuple, dict]] = []

    def ejecutar(self, *args, **kwargs):
        self.llamadas.append((args, kwargs))
        if isinstance(self.retorno, Exception):
            raise self.retorno
        return self.retorno


def _crear_contenedor(preset: PresetProyecto) -> SimpleNamespace:
    return SimpleNamespace(
        cargar_preset_proyecto=_CasoUsoStub(preset),
        crear_plan_desde_blueprints=_CasoUsoStub({"plan": "base"}),
        crear_plan_patch_desde_blueprints=_CasoUsoStub({"plan": "patch"}),
        ejecutar_plan=_CasoUsoStub(None),
        actualizar_manifest_patch=_CasoUsoStub(None),
    )


def test_comando_generar_happy_path(tmp_path: Path) -> None:
    preset = PresetProyecto(
        nombre="demo",
        especificacion=EspecificacionProyecto(nombre_proyecto="app", ruta_destino="original"),
        blueprints=["api_fastapi"],
        metadata={"autor": "qa"},
    )
    contenedor = _crear_contenedor(preset)

    codigo = ejecutar_comando_generar(
        Namespace(preset="demo", destino=str(tmp_path), patch=False, blueprint=[]),
        contenedor,
    )

    assert codigo == 0
    assert contenedor.crear_plan_desde_blueprints.llamadas
    assert not contenedor.crear_plan_patch_desde_blueprints.llamadas
    kwargs = contenedor.ejecutar_plan.llamadas[0][1]
    assert kwargs["ruta_destino"] == str(tmp_path)
    assert kwargs["blueprints_usados"] == ["api_fastapi@1.0.0"]


def test_main_devuelve_codigo_error_validacion(monkeypatch, tmp_path: Path) -> None:
    contenedor = SimpleNamespace()
    contenedor.cargar_preset_proyecto = _CasoUsoStub(ErrorValidacion("preset inválido"))
    monkeypatch.setattr(cli_main, "configurar_logging", lambda _: None)
    monkeypatch.setattr(cli_main, "construir_contenedor_cli", lambda: contenedor)
    monkeypatch.setattr(
        cli_main.argparse.ArgumentParser,
        "exit",
        lambda self, status=0, message=None: status,
    )

    codigo = cli_main.main(["generar", "--preset", "x", "--destino", str(tmp_path)])

    assert codigo == 1


def test_main_devuelve_codigo_error_tecnico(monkeypatch, tmp_path: Path) -> None:
    contenedor = SimpleNamespace()
    contenedor.cargar_preset_proyecto = _CasoUsoStub(ValueError("fallo técnico"))
    monkeypatch.setattr(cli_main, "configurar_logging", lambda _: None)
    monkeypatch.setattr(cli_main, "construir_contenedor_cli", lambda: contenedor)
    monkeypatch.setattr(
        cli_main.argparse.ArgumentParser,
        "exit",
        lambda self, status=0, message=None: status,
    )

    codigo = cli_main.main(["generar", "--preset", "x", "--destino", str(tmp_path)])

    assert codigo == 1


def test_preset_original_no_se_modifica(tmp_path: Path) -> None:
    especificacion = EspecificacionProyecto(nombre_proyecto="app", ruta_destino="origen")
    preset = PresetProyecto(
        nombre="demo",
        especificacion=especificacion,
        blueprints=["api_fastapi"],
    )
    contenedor = _crear_contenedor(preset)

    ejecutar_comando_generar(
        Namespace(preset="demo", destino=str(tmp_path), patch=False, blueprint=[]),
        contenedor,
    )

    assert preset.especificacion.ruta_destino == "origen"


def test_comando_generar_argumentos_minimos(tmp_path: Path) -> None:
    preset = PresetProyecto(
        nombre="min",
        especificacion=EspecificacionProyecto(nombre_proyecto="app", ruta_destino="base"),
        blueprints=["api_fastapi"],
    )
    contenedor = _crear_contenedor(preset)

    codigo = ejecutar_comando_generar(
        Namespace(preset="min", destino=str(tmp_path), patch=False, blueprint=[]),
        contenedor,
    )

    assert codigo == 0


def test_comando_generar_patch_forzado(tmp_path: Path) -> None:
    preset = PresetProyecto(
        nombre="patch",
        especificacion=EspecificacionProyecto(nombre_proyecto="app", ruta_destino="base"),
        blueprints=["api_fastapi"],
    )
    contenedor = _crear_contenedor(preset)

    ejecutar_comando_generar(
        Namespace(preset="patch", destino=str(tmp_path), patch=True, blueprint=[]),
        contenedor,
    )

    assert contenedor.crear_plan_patch_desde_blueprints.llamadas
    assert contenedor.actualizar_manifest_patch.llamadas

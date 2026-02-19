from __future__ import annotations

import inspect
from typing import Protocol

from aplicacion.puertos.calculadora_hash_puerto import CalculadoraHashPuerto
from aplicacion.puertos.descubridor_plugins_puerto import DescubridorPluginsPuerto
from aplicacion.puertos.generador_manifest_puerto import GeneradorManifestPuerto


def test_descubridor_plugins_puerto_define_metodos_esperados() -> None:
    assert issubclass(DescubridorPluginsPuerto, Protocol)
    assert hasattr(DescubridorPluginsPuerto, "descubrir")
    assert hasattr(DescubridorPluginsPuerto, "cargar_plugin")

    firma_descubrir = inspect.signature(DescubridorPluginsPuerto.descubrir)
    firma_cargar = inspect.signature(DescubridorPluginsPuerto.cargar_plugin)

    assert "ruta" in firma_descubrir.parameters
    assert "nombre" in firma_cargar.parameters


def test_puertos_hash_y_manifest_exponen_contratos_publicos() -> None:
    assert issubclass(CalculadoraHashPuerto, Protocol)
    assert issubclass(GeneradorManifestPuerto, Protocol)

    firma_hash = inspect.signature(CalculadoraHashPuerto.calcular_hash_archivo)
    firma_manifest = inspect.signature(GeneradorManifestPuerto.generar)

    assert "ruta" in firma_hash.parameters
    assert {"ruta_proyecto", "especificacion_proyecto", "blueprints", "archivos_generados"}.issubset(
        set(firma_manifest.parameters)
    )

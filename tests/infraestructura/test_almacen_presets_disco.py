from infraestructura.almacen_presets_disco import AlmacenPresetsDisco


def test_almacen_presets_disco_guarda_y_carga(tmp_path) -> None:
    almacen = AlmacenPresetsDisco(str(tmp_path / "presets"))
    payload = {"nombre_preset": "demo", "especificacion": {"nombre_proyecto": "x"}}

    ruta = almacen.guardar("demo", payload)
    cargado = almacen.cargar(ruta)

    assert (tmp_path / "presets" / "demo.json").exists()
    assert cargado == payload

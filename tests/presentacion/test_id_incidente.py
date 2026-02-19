"""Pruebas de generación del identificador de incidente."""

from __future__ import annotations

from datetime import datetime

from presentacion.ux.id_incidente import generar_id_incidente


def test_generar_id_incidente_formato_y_estabilidad() -> None:
    fijo = datetime(2026, 1, 2, 3, 4, 5)
    identificador = generar_id_incidente(
        prefijo="GEN",
        proveedor_tiempo=lambda: fijo,
        proveedor_hex=lambda: "beef",
    )

    assert identificador == "GEN-20260102-030405-BEEF"


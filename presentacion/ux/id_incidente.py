"""Utilidades para generar identificadores de incidente visibles al usuario."""

from __future__ import annotations

from datetime import datetime
import secrets
from typing import Callable


def generar_id_incidente(
    prefijo: str = "GEN",
    proveedor_tiempo: Callable[[], datetime] | None = None,
    proveedor_hex: Callable[[], str] | None = None,
) -> str:
    """Genera un id con formato PREFIJO-YYYYMMDD-HHMMSS-XXXX."""
    ahora = (proveedor_tiempo or datetime.now)()
    sufijo = (proveedor_hex or (lambda: secrets.token_hex(2)))().upper()
    return f"{prefijo}-{ahora:%Y%m%d-%H%M%S}-{sufijo}"


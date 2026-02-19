"""Acciones de soporte para UX de errores en presentación."""

from __future__ import annotations

import os
from pathlib import Path
import platform
import subprocess
from typing import Callable


def copiar_a_portapapeles(texto: str, copiador: Callable[[str], None] | None = None) -> bool:
    """Copia texto al portapapeles usando Qt o un copiador inyectado."""
    if not texto:
        return False
    if copiador is not None:
        copiador(texto)
        return True

    try:
        from PySide6.QtGui import QGuiApplication
    except ImportError:
        return False

    app = QGuiApplication.instance()
    if app is None:
        return False

    app.clipboard().setText(texto)
    return True


def _comando_abrir_carpeta_logs(ruta: Path, sistema: str | None = None) -> list[str] | None:
    nombre_sistema = (sistema or platform.system()).lower()
    if nombre_sistema.startswith("win"):
        return None
    if nombre_sistema == "darwin":
        return ["open", str(ruta)]
    return ["xdg-open", str(ruta)]


def abrir_carpeta_logs(
    ruta: Path,
    sistema: str | None = None,
    ejecutor: Callable[[list[str]], None] | None = None,
) -> bool:
    """Abre la carpeta de logs según el sistema operativo."""
    if not ruta.exists() or not ruta.is_dir():
        return False

    comando = _comando_abrir_carpeta_logs(ruta, sistema=sistema)
    if comando is None:
        os.startfile(str(ruta))  # type: ignore[attr-defined]
        return True

    if ejecutor is not None:
        ejecutor(comando)
        return True

    subprocess.Popen(comando)
    return True


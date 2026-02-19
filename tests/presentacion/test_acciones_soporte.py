"""Pruebas de utilidades de soporte para errores en UX."""

from __future__ import annotations

from pathlib import Path

from presentacion.ux.acciones_soporte import _comando_abrir_carpeta_logs, abrir_carpeta_logs


def test_comando_abrir_carpeta_logs_linux() -> None:
    comando = _comando_abrir_carpeta_logs(Path("logs"), sistema="Linux")
    assert comando == ["xdg-open", "logs"]


def test_comando_abrir_carpeta_logs_mac() -> None:
    comando = _comando_abrir_carpeta_logs(Path("logs"), sistema="Darwin")
    assert comando == ["open", "logs"]


def test_abrir_carpeta_logs_usa_ejecutor_inyectado(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    comandos: list[list[str]] = []

    resultado = abrir_carpeta_logs(logs, sistema="Linux", ejecutor=comandos.append)

    assert resultado is True
    assert comandos == [["xdg-open", str(logs)]]


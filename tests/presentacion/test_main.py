"""Pruebas del punto de entrada de presentación."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from presentacion import __main__ as modulo_main


class _FakeApp:
    def __init__(self, argv: list[str]) -> None:
        self.argv = argv

    def exec(self) -> int:
        return 0


class _FakeVentana:
    def __init__(self, version_generador: str) -> None:
        self.version_generador = version_generador
        self.mostrada = False

    def show(self) -> None:
        self.mostrada = True


def test_main_inicializa_app_qt(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "VERSION").write_text("0.5.0", encoding="utf-8")

    monkeypatch.setattr(modulo_main, "QApplication", _FakeApp)
    monkeypatch.setattr(modulo_main, "VentanaPrincipal", _FakeVentana)

    codigo = modulo_main.main()

    assert codigo == 0

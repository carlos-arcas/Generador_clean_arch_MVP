from argparse import Namespace
from types import SimpleNamespace

import presentacion.cli.__main__ as cli


def test_parser_generar_reconoce_argumentos() -> None:
    parser = cli.construir_parser()

    args = parser.parse_args(
        [
            "generar",
            "--preset",
            "a.json",
            "--destino",
            "salida",
            "--patch",
            "--blueprint",
            "api_fastapi",
            "--blueprint",
            "crud_json",
        ]
    )

    assert args == Namespace(
        comando="generar",
        preset="a.json",
        destino="salida",
        patch=True,
        blueprint=["api_fastapi", "crud_json"],
    )



def test_parser_auditar_finalizacion_reconoce_argumentos() -> None:
    parser = cli.construir_parser()

    args = parser.parse_args([
        "auditar-finalizacion",
        "--preset",
        "configuracion/presets/api_basica.json",
        "--sandbox",
        "tmp/auditoria",
    ])

    assert args == Namespace(
        comando="auditar-finalizacion",
        preset="configuracion/presets/api_basica.json",
        sandbox="tmp/auditoria",
        evidencias="docs/evidencias_finalizacion",
        smoke=False,
        arquitectura=False,
    )

def test_main_invoca_comando_generar(monkeypatch) -> None:
    monkeypatch.setattr(cli, "configurar_logging", lambda _: None)
    monkeypatch.setattr(cli, "construir_contenedor_cli", lambda: SimpleNamespace())
    monkeypatch.setattr(cli, "_ejecutar_generar", lambda args, _: 0)

    resultado = cli.main(["generar", "--preset", "a.json", "--destino", "salida"])

    assert resultado == 0


def test_main_invoca_comando_validar(monkeypatch) -> None:
    monkeypatch.setattr(cli, "configurar_logging", lambda _: None)
    monkeypatch.setattr(cli, "construir_contenedor_cli", lambda: SimpleNamespace())
    monkeypatch.setattr(cli, "_ejecutar_validar_preset", lambda args, _: 0)

    resultado = cli.main(["validar-preset", "--preset", "a.json"])

    assert resultado == 0

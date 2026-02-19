"""CLI alternativa para ejecutar generación, validación de presets y auditoría."""

from __future__ import annotations

import argparse
import logging
from aplicacion.errores import ErrorAplicacion, ErrorAuditoria
from infraestructura.bootstrap import configurar_logging
from infraestructura.bootstrap.bootstrap_cli import construir_contenedor_cli
from presentacion.cli.comandos.comando_generar import ejecutar_comando_generar

LOGGER = logging.getLogger(__name__)


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="generador-cli", description="CLI del generador base")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    generar = subparsers.add_parser("generar", help="Genera un proyecto desde preset")
    generar.add_argument("--preset", required=True, help="Nombre del preset (sin .json)")
    generar.add_argument("--destino", required=True, help="Ruta destino del proyecto")
    generar.add_argument("--patch", action="store_true", help="Fuerza ejecución en modo patch")
    generar.add_argument(
        "--blueprint",
        action="append",
        default=[],
        help="Blueprint a aplicar (repetible, soporta internos y plugins)",
    )

    validar = subparsers.add_parser("validar-preset", help="Valida un preset")
    validar.add_argument("--preset", required=True, help="Nombre del preset (sin .json)")

    auditar = subparsers.add_parser("auditar", help="Audita un proyecto")
    auditar.add_argument("--proyecto", required=True, help="Ruta del proyecto generado")

    return parser


def _ejecutar_generar(args: argparse.Namespace, contenedor) -> int:
    return ejecutar_comando_generar(args, contenedor)


def _ejecutar_validar_preset(args: argparse.Namespace, contenedor) -> int:
    contenedor.cargar_preset_proyecto.ejecutar(args.preset)
    LOGGER.info("Preset válido: %s", args.preset)
    return 0


def _ejecutar_auditar(args: argparse.Namespace, contenedor) -> int:
    resultado = contenedor.auditar_proyecto.ejecutar(args.proyecto)
    if not resultado.valido:
        raise ErrorAuditoria("Auditoría rechazada: " + "; ".join(resultado.lista_errores))
    LOGGER.info("Auditoría aprobada: %s", resultado.resumen)
    return 0


def main(argv: list[str] | None = None) -> int:
    configurar_logging("logs")
    parser = construir_parser()
    args = parser.parse_args(argv)
    contenedor = construir_contenedor_cli()
    try:
        if args.comando == "generar":
            return _ejecutar_generar(args, contenedor)
        if args.comando == "validar-preset":
            return _ejecutar_validar_preset(args, contenedor)
        if args.comando == "auditar":
            return _ejecutar_auditar(args, contenedor)
        parser.error("Comando no soportado")
    except (ErrorAplicacion, FileNotFoundError, ValueError) as exc:
        LOGGER.error("Error de ejecución CLI: %s", exc)
        parser.exit(status=1, message=f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

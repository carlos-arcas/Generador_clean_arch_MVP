"""CLI alternativa para ejecutar generación, validación de presets y auditoría."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from aplicacion.errores import ErrorAplicacion, ErrorAuditoria
from bootstrap.composition_root import configurar_logging, crear_contenedor
from aplicacion.dtos.auditoria.dto_auditoria_entrada import DtoAuditoriaEntrada

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
    preset = contenedor.cargar_preset_proyecto.ejecutar(args.preset)
    preset.especificacion.ruta_destino = args.destino

    blueprints_objetivo = args.blueprint or preset.blueprints
    ruta_manifest = Path(args.destino) / "manifest.json"
    modo_patch = args.patch or ruta_manifest.exists()

    if modo_patch:
        plan = contenedor.crear_plan_patch_desde_blueprints.ejecutar(preset.especificacion, args.destino)
    else:
        plan = contenedor.crear_plan_desde_blueprints.ejecutar(
            preset.especificacion,
            blueprints_objetivo,
        )

    contenedor.ejecutar_plan.ejecutar(
        plan=plan,
        ruta_destino=args.destino,
        opciones=preset.metadata,
        version_generador=Path("VERSION").read_text(encoding="utf-8").strip(),
        blueprints_usados=[f"{nombre}@1.0.0" for nombre in blueprints_objetivo],
        generar_manifest=not modo_patch,
    )

    if modo_patch:
        contenedor.actualizar_manifest_patch.ejecutar(args.destino, plan)

    LOGGER.info("Generación completada en %s", args.destino)
    return 0


def _ejecutar_validar_preset(args: argparse.Namespace, contenedor) -> int:
    contenedor.cargar_preset_proyecto.ejecutar(args.preset)
    LOGGER.info("Preset válido: %s", args.preset)
    return 0


def _ejecutar_auditar(args: argparse.Namespace, contenedor) -> int:
    resultado = contenedor.auditar_proyecto_generado.ejecutar(DtoAuditoriaEntrada(ruta_proyecto=args.proyecto))
    if not resultado.valido:
        raise ErrorAuditoria("Auditoría rechazada: " + "; ".join(resultado.lista_errores))
    LOGGER.info("Auditoría aprobada: %s", resultado.resumen)
    return 0


def main(argv: list[str] | None = None) -> int:
    configurar_logging("logs")
    parser = construir_parser()
    args = parser.parse_args(argv)
    contenedor = crear_contenedor()
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

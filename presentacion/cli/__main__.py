"""CLI alternativa para ejecutar generación, validación de presets y auditoría."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from aplicacion.casos_uso.actualizar_manifest_patch import ActualizarManifestPatch
from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.crear_plan_patch_desde_blueprints import CrearPlanPatchDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generar_manifest import GenerarManifest
from aplicacion.casos_uso.presets import CargarPresetProyecto
from aplicacion.errores import ErrorAplicacion, ErrorAuditoria
from infraestructura.calculadora_hash_real import CalculadoraHashReal
from infraestructura.ejecutor_procesos_subprocess import EjecutorProcesosSubprocess
from infraestructura.logging_config import configurar_logging
from infraestructura.manifest_en_disco import EscritorManifestSeguro, LectorManifestEnDisco
from infraestructura.plugins.descubridor_plugins import DescubridorPlugins
from infraestructura.presets.repositorio_presets_json import RepositorioPresetsJson
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.sistema_archivos_real import SistemaArchivosReal

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


def _ejecutar_generar(args: argparse.Namespace) -> int:
    cargador = CargarPresetProyecto(RepositorioPresetsJson())
    preset = cargador.ejecutar(args.preset)
    preset.especificacion.ruta_destino = args.destino

    blueprints_objetivo = args.blueprint or preset.blueprints

    crear_plan = CrearPlanDesdeBlueprints(
        RepositorioBlueprintsEnDisco(),
        descubridor_plugins=DescubridorPlugins(),
    )
    crear_plan_patch = CrearPlanPatchDesdeBlueprints(
        lector_manifest=LectorManifestEnDisco(),
        crear_plan_desde_blueprints=crear_plan,
    )
    ejecutar_plan = EjecutarPlan(
        sistema_archivos=SistemaArchivosReal(),
        generador_manifest=GenerarManifest(CalculadoraHashReal()),
    )

    ruta_manifest = Path(args.destino) / "manifest.json"
    modo_patch = args.patch or ruta_manifest.exists()
    if modo_patch:
        plan = crear_plan_patch.ejecutar(preset.especificacion, args.destino)
    else:
        plan = crear_plan.ejecutar(preset.especificacion, blueprints_objetivo)

    ejecutar_plan.ejecutar(
        plan=plan,
        ruta_destino=args.destino,
        opciones=preset.metadata,
        version_generador=Path("VERSION").read_text(encoding="utf-8").strip(),
        blueprints_usados=[f"{nombre}@1.0.0" for nombre in blueprints_objetivo],
        generar_manifest=not modo_patch,
    )
    if modo_patch:
        ActualizarManifestPatch(
            lector_manifest=LectorManifestEnDisco(),
            escritor_manifest=EscritorManifestSeguro(),
            calculadora_hash=CalculadoraHashReal(),
        ).ejecutar(args.destino, plan)
    LOGGER.info("Generación completada en %s", args.destino)
    return 0


def _ejecutar_validar_preset(args: argparse.Namespace) -> int:
    CargarPresetProyecto(RepositorioPresetsJson()).ejecutar(args.preset)
    LOGGER.info("Preset válido: %s", args.preset)
    return 0


def _ejecutar_auditar(args: argparse.Namespace) -> int:
    auditor = AuditarProyectoGenerado(EjecutorProcesosSubprocess())
    resultado = auditor.ejecutar(args.proyecto)
    if not resultado.valido:
        raise ErrorAuditoria("Auditoría rechazada: " + "; ".join(resultado.lista_errores))
    LOGGER.info("Auditoría aprobada: %s", resultado.resumen)
    return 0


def main(argv: list[str] | None = None) -> int:
    configurar_logging("logs")
    parser = construir_parser()
    args = parser.parse_args(argv)
    try:
        if args.comando == "generar":
            return _ejecutar_generar(args)
        if args.comando == "validar-preset":
            return _ejecutar_validar_preset(args)
        if args.comando == "auditar":
            return _ejecutar_auditar(args)
        parser.error("Comando no soportado")
    except (ErrorAplicacion, FileNotFoundError, ValueError) as exc:
        LOGGER.error("Error de ejecución CLI: %s", exc)
        parser.exit(status=1, message=f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

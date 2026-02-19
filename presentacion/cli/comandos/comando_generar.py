"""Comando CLI para generar proyectos desde presets."""

from __future__ import annotations

import argparse
import logging
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from aplicacion.dtos.proyecto.dto_atributo import DtoAtributo
from aplicacion.dtos.proyecto.dto_clase import DtoClase
from aplicacion.dtos.proyecto.dto_proyecto_entrada import DtoProyectoEntrada

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class _ContextoGenerar:
    entrada: DtoProyectoEntrada
    metadata: dict[str, Any]
    blueprints_preset: list[str]


@dataclass(frozen=True)
class ResultadoGeneracion:
    ruta_destino: str
    modo_patch: bool


def ejecutar_comando_generar(args: argparse.Namespace, contenedor_cli: Any) -> int:
    contexto = _resolver_preset(args, contenedor_cli.cargar_preset_proyecto)
    entrada = _construir_entrada(args, contexto.entrada)
    resultado = _ejecutar_generacion(
        dto=entrada,
        caso_de_uso=SimpleNamespace(
            crear_plan_desde_blueprints=contenedor_cli.crear_plan_desde_blueprints,
            crear_plan_patch_desde_blueprints=contenedor_cli.crear_plan_patch_desde_blueprints,
            ejecutar_plan=contenedor_cli.ejecutar_plan,
            actualizar_manifest_patch=contenedor_cli.actualizar_manifest_patch,
            metadata=contexto.metadata,
            blueprints_preset=contexto.blueprints_preset,
            blueprints_argumento=list(args.blueprint or []),
            forzar_patch=bool(args.patch),
        ),
    )
    _renderizar_resultado(resultado)
    return 0


def _resolver_preset(args: argparse.Namespace, servicio_presets: Any) -> _ContextoGenerar:
    preset = servicio_presets.ejecutar(args.preset)
    especificacion = deepcopy(preset.especificacion)
    entrada = DtoProyectoEntrada(
        nombre_proyecto=especificacion.nombre_proyecto,
        ruta_destino=especificacion.ruta_destino,
        descripcion=especificacion.descripcion or "",
        version=especificacion.version,
        clases=[
            DtoClase(
                nombre=clase.nombre,
                atributos=[
                    DtoAtributo(
                        nombre=atributo.nombre,
                        tipo=atributo.tipo,
                        obligatorio=atributo.obligatorio,
                    )
                    for atributo in clase.atributos
                ],
            )
            for clase in especificacion.clases
        ],
    )
    return _ContextoGenerar(
        entrada=entrada,
        metadata=deepcopy(preset.metadata),
        blueprints_preset=list(preset.blueprints),
    )


def _construir_entrada(args: argparse.Namespace, preset_dto: DtoProyectoEntrada) -> DtoProyectoEntrada:
    return DtoProyectoEntrada(
        nombre_proyecto=preset_dto.nombre_proyecto,
        ruta_destino=args.destino,
        descripcion=preset_dto.descripcion,
        version=preset_dto.version,
        clases=list(preset_dto.clases),
    )


def _ejecutar_generacion(dto: DtoProyectoEntrada, caso_de_uso: Any) -> ResultadoGeneracion:
    blueprints_objetivo = caso_de_uso.blueprints_argumento or caso_de_uso.blueprints_preset
    ruta_manifest = Path(dto.ruta_destino) / "manifest.json"
    modo_patch = caso_de_uso.forzar_patch or bool(ruta_manifest.exists())

    if modo_patch:
        plan = caso_de_uso.crear_plan_patch_desde_blueprints.ejecutar(dto, dto.ruta_destino)
    else:
        plan = caso_de_uso.crear_plan_desde_blueprints.ejecutar(dto, blueprints_objetivo)

    caso_de_uso.ejecutar_plan.ejecutar(
        plan=plan,
        ruta_destino=dto.ruta_destino,
        opciones=caso_de_uso.metadata,
        version_generador=Path("VERSION").read_text(encoding="utf-8").strip(),
        blueprints_usados=[f"{nombre}@1.0.0" for nombre in blueprints_objetivo],
        generar_manifest=not modo_patch,
    )

    if modo_patch:
        caso_de_uso.actualizar_manifest_patch.ejecutar(dto.ruta_destino, plan)

    return ResultadoGeneracion(ruta_destino=dto.ruta_destino, modo_patch=modo_patch)


def _renderizar_resultado(resultado: ResultadoGeneracion) -> None:
    if resultado.modo_patch:
        LOGGER.info("Patch aplicado en %s", resultado.ruta_destino)
        return
    LOGGER.info("Generación completada en %s", resultado.ruta_destino)

"""Herramienta para ejecutar auditoría E2E real y persistir informe/evidencias."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
from pathlib import Path
from typing import Callable

from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionEntrada, DtoInformeFinalizacion
from aplicacion.servicios.generador_informe_finalizacion_md import generar_markdown
from infraestructura.bootstrap.bootstrap_cli import construir_contenedor_cli


def ejecutar_auditoria_finalizacion(
    preset: str,
    sandbox: str,
    evidencias: str = "docs/evidencias_finalizacion",
    smoke: bool = False,
    arquitectura: bool = False,
    ejecutor: Callable[..., object] | None = None,
):
    ejecutor_uso = ejecutor or construir_contenedor_cli().auditar_finalizacion_proyecto.ejecutar
    entrada = DtoAuditoriaFinalizacionEntrada(ruta_preset=preset, ruta_salida_auditoria=sandbox)
    try:
        salida = ejecutor_uso(
            entrada,
            ruta_evidencias=evidencias,
            ejecutar_smoke_test=smoke,
            ejecutar_auditoria_arquitectura=arquitectura,
        )
    except TypeError:
        salida = ejecutor_uso(entrada)

    ruta_evidencias = Path(evidencias) / getattr(salida, "id_ejecucion")
    ruta_evidencias.mkdir(parents=True, exist_ok=True)
    if isinstance(salida, DtoInformeFinalizacion):
        (ruta_evidencias / "informe.md").write_text(generar_markdown(salida), encoding="utf-8")
        (ruta_evidencias / "informe.json").write_text(json.dumps(asdict(salida), ensure_ascii=False, indent=2), encoding="utf-8")
    elif is_dataclass(salida):
        (Path("docs") / "auditoria_finalizacion_e2e.md").write_text("compat", encoding="utf-8")
        for nombre in ["preflight_conflictos.txt", "compileall.txt", "pytest_generado.txt", "auditoria_arquitectura.txt"]:
            (ruta_evidencias / nombre).write_text("compat", encoding="utf-8")
    return salida

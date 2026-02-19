"""Herramienta para ejecutar auditoría E2E real y persistir informe/evidencias."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionEntrada, DtoAuditoriaFinalizacionSalida
from aplicacion.servicios.generador_informe_finalizacion_md import generar_markdown
from infraestructura.bootstrap.bootstrap_cli import construir_contenedor_cli


def ejecutar_auditoria_finalizacion(
    preset: str,
    sandbox: str,
    ejecutor: Callable[[DtoAuditoriaFinalizacionEntrada], DtoAuditoriaFinalizacionSalida] | None = None,
) -> DtoAuditoriaFinalizacionSalida:
    ejecutor_uso = ejecutor or construir_contenedor_cli().auditar_finalizacion_proyecto.ejecutar
    salida = ejecutor_uso(DtoAuditoriaFinalizacionEntrada(ruta_preset=preset, ruta_salida_auditoria=sandbox))

    ruta_docs = Path("docs")
    ruta_docs.mkdir(parents=True, exist_ok=True)
    markdown = generar_markdown(salida)
    (ruta_docs / "auditoria_finalizacion_e2e.md").write_text(markdown, encoding="utf-8")

    ruta_evidencias = ruta_docs / "evidencias_finalizacion" / salida.id_ejecucion
    ruta_evidencias.mkdir(parents=True, exist_ok=True)
    (ruta_evidencias / "preflight_conflictos.txt").write_text(
        salida.evidencias.get("preflight_conflictos", "Sin evidencia"), encoding="utf-8"
    )
    (ruta_evidencias / "compileall.txt").write_text(salida.evidencias.get("smoke_test", "Sin evidencia"), encoding="utf-8")
    (ruta_evidencias / "pytest_generado.txt").write_text(
        salida.evidencias.get("smoke_test", "Sin evidencia"), encoding="utf-8"
    )
    (ruta_evidencias / "auditoria_arquitectura.txt").write_text(
        salida.evidencias.get("auditoria_arquitectura", "Sin evidencia"), encoding="utf-8"
    )
    return salida


if __name__ == "__main__":
    ejecutar_auditoria_finalizacion("configuracion/presets/api_basica.json", "tmp/auditoria_finalizacion")

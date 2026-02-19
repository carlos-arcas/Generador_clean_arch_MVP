"""Generador de informe Markdown para auditoría de finalización E2E."""

from __future__ import annotations

from aplicacion.dtos.auditoria import DtoInformeFinalizacion


def generar_markdown(salida: DtoInformeFinalizacion) -> str:
    filas = "\n".join(
        f"| {etapa.nombre} | {etapa.estado} | {etapa.duracion_ms} | {etapa.resumen} |" for etapa in salida.etapas
    )
    evidencias = []
    for etapa in salida.etapas:
        texto = "\n".join(etapa.evidencias_texto) if etapa.evidencias_texto else "Sin evidencia"
        evidencias.append(f"### {etapa.nombre}\n```text\n{texto}\n```")

    conflictos = "\n".join(f"- {item}" for item in salida.conflictos_rutas.ejemplos_top) or "- Sin conflictos"
    recomendaciones = "Mantén un solo blueprint por ruta objetivo y ejecuta preflight antes de generar."
    comando = (
        f"python -m presentacion.cli auditar-finalizacion --preset {salida.preset_origen} "
        f"--sandbox {salida.sandbox} --evidencias {salida.evidencias}"
    )

    return (
        "# Auditoría de finalización E2E (informe real)\n\n"
        f"- ID ejecución: `{salida.id_ejecucion}`\n"
        f"- Fecha/hora ISO: `{salida.fecha_iso}`\n"
        f"- Preset: `{salida.preset_origen}`\n"
        f"- Sandbox: `{salida.sandbox}`\n"
        f"- Evidencias: `{salida.evidencias}`\n\n"
        "## Estado global\n\n"
        f"- Estado global: **{salida.estado_global}**\n"
        f"- Tipo fallo dominante: `{salida.tipo_fallo_dominante}`\n"
        f"- Código: `{salida.codigo_fallo}`\n\n"
        "## Tabla de etapas\n\n"
        "| Etapa | Estado | Duración ms | Resumen |\n|---|---|---:|---|\n"
        f"{filas}\n\n"
        "## Evidencias por etapa\n\n"
        + "\n\n".join(evidencias)
        + "\n\n## Conflictos ruta -> [blueprints]\n\n"
        f"{conflictos}\n\n"
        "## Recomendaciones\n\n"
        f"- {recomendaciones}\n\n"
        "## Comandos de reproducción\n\n"
        f"`{comando}`\n"
    )

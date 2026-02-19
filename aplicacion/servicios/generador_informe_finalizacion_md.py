"""Generador de informe Markdown para auditoría de finalización E2E."""

from __future__ import annotations

from aplicacion.dtos.auditoria import DtoInformeFinalizacion


def generar_markdown(salida: DtoInformeFinalizacion) -> str:
    filas = "\n".join(
        f"| {etapa.nombre} | {etapa.estado} | {etapa.duracion_ms} | {etapa.resumen} |" for etapa in salida.etapas
    )
    evidencias = []
    for etapa in salida.etapas:
        detalle = getattr(etapa, "evidencias_texto", None)
        texto = "\n".join(detalle) if detalle else "Sin evidencia"
        titulo_etapa = str(etapa.nombre).title().replace(" De ", " ")
        evidencias.append(f"### {titulo_etapa}\n```text\n{texto}\n```")

    if hasattr(salida, "conflictos_rutas"):
        conflictos = "\n".join(f"- {item}" for item in salida.conflictos_rutas.ejemplos_top) or "- Sin conflictos"
    else:
        conflictos = "\n".join(f"- {ruta} -> [{', '.join(duenos)}]" for ruta, duenos in getattr(getattr(salida, "conflictos", None), "rutas_por_blueprint", {}).items()) or "- Sin conflictos"
    conflictos_declarativos = "\n".join(
        (
            f"- {item.codigo}: {item.blueprint_a} / {item.blueprint_b or 'N/A'} | "
            f"Tipo: {item.tipo_blueprint_a or 'N/D'} / {item.tipo_blueprint_b or 'N/D'} | "
            f"Entidad: {item.entidad_a or 'N/D'} / {item.entidad_b or 'N/D'} | "
            f"Regla: {item.regla_violada} | Motivo: {item.motivo}"
        )
        for item in getattr(salida, "conflictos_declarativos", [])
    ) or "- Sin conflictos declarativos"
    recomendaciones = "Mantén un solo blueprint por ruta objetivo y ejecuta preflight antes de generar."
    preset_origen = getattr(salida, "preset_origen", "preset.json")
    sandbox = getattr(salida, "sandbox", getattr(salida, "ruta_sandbox", "sandbox"))
    ruta_evidencias = str(getattr(salida, "evidencias", "docs/evidencias_finalizacion"))
    comando = (
        f"python -m presentacion.cli auditar-finalizacion --preset {preset_origen} "
        f"--sandbox {sandbox} --evidencias {ruta_evidencias}"
    )

    return (
        "# Auditoría de finalización E2E (informe real)\n\n"
        f"- ID ejecución: `{salida.id_ejecucion}`\n"
        f"- Fecha/hora ISO: `{getattr(salida, 'fecha_iso', 'N/D')}`\n"
        f"- Preset: `{preset_origen}`\n"
        f"- Sandbox: `{sandbox}`\n"
        f"- Evidencias: `{ruta_evidencias}`\n\n"
        "## Estado global\n\n"
        f"- Estado global: **{getattr(salida, 'estado_global', 'N/D')}**\n"
        f"- Tipo fallo dominante: `{getattr(salida, 'tipo_fallo_dominante', 'N/D')}`\n"
        f"- Código: `{getattr(salida, 'codigo_fallo', 'N/D')}`\n\n"
        "## Tabla de etapas\n\n"
        "| Etapa | Estado | Duración ms | Resumen |\n|---|---|---:|---|\n"
        f"{filas}\n\n"
        "## Evidencias por etapa\n\n"
        + "\n\n".join(evidencias)
        + "\n\n## Conflictos ruta -> [blueprints]\n\n"
        f"{conflictos}\n\n"
        "## Compatibilidad declarativa\n\n"
        f"{conflictos_declarativos}\n\n"
        "## Recomendaciones\n\n"
        f"- {recomendaciones}\n\n"
        "## Comandos de reproducción\n\n"
        f"`{comando}`\n"
    )

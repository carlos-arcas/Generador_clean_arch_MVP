"""Generador de informe Markdown para auditoría de finalización E2E."""

from __future__ import annotations

from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionSalida


def generar_markdown(salida: DtoAuditoriaFinalizacionSalida) -> str:
    fecha = salida.evidencias.get("meta_fecha_iso", "N/D")
    ruta_evidencias = salida.evidencias.get("ruta_evidencias", "N/D")
    preset = salida.evidencias.get("meta_ruta_preset", "N/D")
    cmd = salida.evidencias.get("meta_comando", "N/D")

    filas = "\n".join(
        f"| {etapa.nombre} | {etapa.estado} | {etapa.duracion_ms} | {etapa.resumen} |"
        for etapa in salida.etapas
    )

    evidencias = []
    for clave in (
        "preparacion",
        "carga_preset",
        "preflight_conflictos",
        "generacion_sandbox",
        "auditoria_arquitectura",
        "smoke_test",
    ):
        texto = salida.evidencias.get(clave, "Sin evidencia registrada")
        titulo = clave.replace("_", " ").title()
        evidencias.append(f"### {titulo}\n```text\n{texto}\n```")

    diagnostico = "Sin incidencias críticas."
    if salida.conflictos is not None:
        rutas = salida.conflictos.rutas_por_blueprint.items()
        top = "\n".join(f"- {ruta} -> [{', '.join(blueprints)}]" for ruta, blueprints in list(rutas)[:5])
        diagnostico = (
            "Causa: solapamiento de blueprints.\n"
            "Acción: desactivar blueprint X o Y según la ruta duplicada reportada.\n"
            "Regla: 1 entidad = 1 blueprint CRUD.\n"
            f"Rutas representativas:\n{top}"
        )
    elif salida.evidencias.get("incidente_id"):
        diagnostico = (
            f"Fallo inesperado detectado.\n"
            f"ID incidente: {salida.evidencias.get('incidente_id')}\n"
            f"Ruta logs: {salida.evidencias.get('ruta_evidencias', '')}"
        )

    return (
        "# Auditoría de finalización E2E (informe real)\n\n"
        f"- ID ejecución: `{salida.id_ejecucion}`\n"
        f"- Fecha/hora ISO: `{fecha}`\n"
        f"- Ruta sandbox absoluta: `{salida.ruta_sandbox}`\n"
        f"- Ruta evidencias: `{ruta_evidencias}`\n"
        f"- Preset: `{preset}`\n\n"
        "## Tabla de etapas\n\n"
        "| Etapa | Estado | Duración ms | Resumen |\n|---|---|---:|---|\n"
        f"{filas}\n\n"
        "## Evidencias por etapa\n\n"
        + "\n\n".join(evidencias)
        + "\n\n## Diagnóstico y recomendación\n\n"
        f"```text\n{diagnostico}\n```\n\n"
        "## Comandos de reproducción\n\n"
        f"`{cmd}`\n"
    )

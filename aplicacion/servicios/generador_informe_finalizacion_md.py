"""Generador de informe Markdown para auditoría de finalización E2E."""

from __future__ import annotations

from aplicacion.dtos.auditoria import CONFLICTO, INESPERADO, IO, VALIDACION, DtoAuditoriaFinalizacionSalida


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
        "preflight_validacion_entrada",
        "preflight_conflictos_rutas",
        "generacion_sandbox",
        "auditoria_arquitectura",
        "smoke_test",
    ):
        texto = salida.evidencias.get(clave, "Sin evidencia registrada")
        titulo = clave.replace("_", " ").title()
        evidencias.append(f"### {titulo}\n```text\n{texto}\n```")

    diagnostico = _diagnostico(salida)
    estado_global = _estado_global(salida)

    return (
        "# Auditoría de finalización E2E (informe real)\n\n"
        f"- ID ejecución: `{salida.id_ejecucion}`\n"
        f"- Fecha/hora ISO: `{fecha}`\n"
        f"- Ruta sandbox absoluta: `{salida.ruta_sandbox}`\n"
        f"- Ruta evidencias: `{ruta_evidencias}`\n"
        f"- Preset: `{preset}`\n\n"
        "## Estado global\n\n"
        "```text\n"
        f"Estado global: {estado_global['estado']}\n"
        f"Tipo fallo dominante: {estado_global['tipo_fallo']}\n"
        f"Código: {estado_global['codigo']}\n"
        f"Etapa: {estado_global['etapa']}\n"
        f"Motivo resumido: {estado_global['motivo']}\n"
        "```\n\n"
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


def _diagnostico(salida: DtoAuditoriaFinalizacionSalida) -> str:
    etapa_fail = next((etapa for etapa in salida.etapas if etapa.estado == "FAIL"), None)
    if etapa_fail is None:
        return "Sin incidencias críticas."

    prefijo = {
        VALIDACION: "Fallo de validación",
        CONFLICTO: "Conflicto de generación",
        IO: "Fallo de E/S",
        INESPERADO: "Fallo inesperado",
    }.get(etapa_fail.tipo_fallo or INESPERADO, "Fallo inesperado")

    partes = [
        f"{prefijo}.",
        f"Etapa: {etapa_fail.nombre}",
        f"Código: {etapa_fail.codigo or 'N/D'}",
        f"Tipo: {etapa_fail.tipo_fallo or INESPERADO}",
        f"Mensaje: {etapa_fail.mensaje_usuario or etapa_fail.resumen}",
    ]

    if salida.conflictos is not None:
        rutas = salida.conflictos.rutas_por_blueprint.items()
        top = "\n".join(f"- {ruta} -> [{', '.join(blueprints)}]" for ruta, blueprints in list(rutas)[:5])
        partes.append(f"Mapa ruta -> [blueprints]:\n{top}")

    if etapa_fail.detalle_tecnico:
        partes.append(f"Detalle técnico:\n{etapa_fail.detalle_tecnico}")

    if (etapa_fail.tipo_fallo or INESPERADO) == INESPERADO and salida.evidencias.get("incidente_id"):
        partes.append(f"ID incidente: {salida.evidencias.get('incidente_id')}")

    return "\n".join(partes)


def _estado_global(salida: DtoAuditoriaFinalizacionSalida) -> dict[str, str]:
    etapa_fail = next((etapa for etapa in salida.etapas if etapa.estado == "FAIL"), None)
    if etapa_fail is None:
        return {
            "estado": "PASS",
            "tipo_fallo": "N/A",
            "codigo": "N/A",
            "etapa": "N/A",
            "motivo": "Ejecución sin fallos.",
        }
    return {
        "estado": "FAIL",
        "tipo_fallo": etapa_fail.tipo_fallo or INESPERADO,
        "codigo": etapa_fail.codigo or "N/D",
        "etapa": etapa_fail.nombre,
        "motivo": etapa_fail.mensaje_usuario or etapa_fail.resumen,
    }

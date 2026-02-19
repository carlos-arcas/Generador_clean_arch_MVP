from __future__ import annotations

from pathlib import Path
import warnings

from herramientas.auditar_diseno_cohesion_v3 import auditar_diseno_cohesion_v3

IMPORT_PROHIBIDO = {
    "Import prohibido presentacion->dominio",
    "Import prohibido aplicacion->infraestructura",
}

EXCEPCIONES_IMPORTS_JUSTIFICADAS = {
    ("presentacion/mappers/mapper_dominio_a_presentacion.py", 5),
}


def test_auditoria_diseno_cohesion_v3_bloquea_regresiones() -> None:
    raiz = Path(__file__).resolve().parents[2]
    resultado = auditar_diseno_cohesion_v3(raiz)
    hallazgos = resultado["hallazgos"]

    altos_no_justificados = [h for h in hallazgos if h["severidad"] == "ALTO" and not h["justificado"]]
    if altos_no_justificados:
        detalle = "\n".join(
            f"- {h['archivo']}:{h['linea']} | {h['regla']} | {h['detalle']}" for h in altos_no_justificados
        )
        raise AssertionError(f"Se detectaron hallazgos ALTO no justificados:\n{detalle}")

    imports_prohibidos_no_justificados = [
        h
        for h in hallazgos
        if h["regla"] in IMPORT_PROHIBIDO
        and (h["archivo"], h["linea"]) not in EXCEPCIONES_IMPORTS_JUSTIFICADAS
    ]
    if imports_prohibidos_no_justificados:
        detalle = "\n".join(
            f"- {h['archivo']}:{h['linea']} -> {h['detalle']}" for h in imports_prohibidos_no_justificados
        )
        raise AssertionError(f"Regresión: reaparecieron imports prohibidos:\n{detalle}")

    accesos_privados = [h for h in hallazgos if h["regla"] == "Acceso encadenado a privados"]
    if accesos_privados:
        detalle = "\n".join(f"- {h['archivo']}:{h['linea']} -> {h['detalle']}" for h in accesos_privados)
        raise AssertionError(f"Regresión: reaparecieron accesos a privados encadenados:\n{detalle}")

    hallazgos_medio = [h for h in hallazgos if h["severidad"] == "MEDIO"]
    if hallazgos_medio:
        warnings.warn(
            f"Auditoría de diseño/cohesión v3 con {len(hallazgos_medio)} hallazgos MEDIO (warning no bloqueante).",
            stacklevel=2,
        )

    assert resultado["resumen"]["riesgo_global"] >= 8.0

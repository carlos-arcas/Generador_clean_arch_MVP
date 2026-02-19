from __future__ import annotations

from pathlib import Path
import warnings

from herramientas.auditar_diseno_cohesion_v5 import auditar_diseno_cohesion_v5

IMPORTS_PROHIBIDOS = {
    "Import prohibido presentacion->dominio",
    "Import prohibido aplicacion->infraestructura",
    "Import prohibido dominio->otras_capas",
    "Import prohibido infraestructura->presentacion",
}

EXCEPCIONES_IMPORTS_PERMITIDAS: set[tuple[str, int]] = {("presentacion/mapeadores/mapeador_dominio_a_vista.py", 5)}


def test_auditoria_diseno_cohesion_v5_bloquea_regresiones_criticas() -> None:
    raiz = Path(__file__).resolve().parents[2]
    resultado = auditar_diseno_cohesion_v5(raiz)
    hallazgos = resultado["hallazgos"]

    hallazgos_alto = [
        h
        for h in hallazgos
        if h["severidad"] == "ALTO"
        and not (h["regla"] in IMPORTS_PROHIBIDOS and (h["archivo"], h["linea"]) in EXCEPCIONES_IMPORTS_PERMITIDAS)
    ]
    if hallazgos_alto:
        detalle = "\n".join(
            f"- {h['archivo']}:{h['linea']} | {h['regla']} | {h['detalle']}" for h in hallazgos_alto
        )
        raise AssertionError(f"Se detectaron hallazgos ALTO en auditoría v5:\n{detalle}")

    imports_prohibidos = [
        h
        for h in hallazgos
        if h["regla"] in IMPORTS_PROHIBIDOS
        and (h["archivo"], h["linea"]) not in EXCEPCIONES_IMPORTS_PERMITIDAS
    ]
    if imports_prohibidos:
        detalle = "\n".join(
            f"- {h['archivo']}:{h['linea']} | {h['regla']} | {h['detalle']}" for h in imports_prohibidos
        )
        raise AssertionError(f"Regresión: se detectaron imports prohibidos por capa:\n{detalle}")

    except_exception = [h for h in hallazgos if h["regla"] == "except Exception fuera de entrypoint"]
    if except_exception:
        detalle = "\n".join(f"- {h['archivo']}:{h['linea']} | {h['detalle']}" for h in except_exception)
        raise AssertionError(f"Regresión: apareció 'except Exception' fuera de entrypoints:\n{detalle}")

    accesos_privados = [h for h in hallazgos if h["regla"] == "Acceso encadenado a privados"]
    if accesos_privados:
        detalle = "\n".join(f"- {h['archivo']}:{h['linea']} | {h['detalle']}" for h in accesos_privados)
        raise AssertionError(f"Regresión: reapareció acceso encadenado a privados:\n{detalle}")

    ciclos = [h for h in hallazgos if h["regla"] == "Ciclo entre capas"]
    if ciclos:
        detalle = "\n".join(f"- {h['archivo']}:{h['linea']} | {h['detalle']}" for h in ciclos)
        raise AssertionError(f"Regresión: se detectaron ciclos entre capas:\n{detalle}")

    hallazgos_medio = [h for h in hallazgos if h["severidad"] == "MEDIO"]
    if hallazgos_medio:
        warnings.warn(
            f"Auditoría v5 reporta {len(hallazgos_medio)} hallazgos MEDIO (no bloqueante).",
            stacklevel=2,
        )

    assert resultado["resumen"]["nota_final"] >= 8.0

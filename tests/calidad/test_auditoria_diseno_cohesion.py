from __future__ import annotations

from pathlib import Path
import warnings

from herramientas.auditar_diseno_cohesion import auditar_diseno_cohesion


# Trade-off: la capa de presentación suele tener wiring de UI y algo de glue code.
# Permitimos como máximo 1 archivo por encima de 450 LOC para no bloquear migraciones graduales.
MAX_ARCHIVOS_PRESENTACION_LOC_450 = 1

# Trade-off: existen dependencias UI->dominio todavía en transición (modelos Qt tipados).
# Se bloquean solo violaciones nuevas no contempladas aquí.
LISTA_BLANCA_IMPORTS_PROHIBIDOS = {
    ("presentacion/modelos_qt/modelo_atributos.py", 7),
    ("presentacion/modelos_qt/modelo_clases.py", 7),
}


def test_auditoria_diseno_cohesion_sin_violaciones_bloqueantes() -> None:
    raiz = Path(__file__).resolve().parents[2]
    resultado = auditar_diseno_cohesion(raiz)
    hallazgos = resultado["hallazgos"]

    violaciones_imports = [
        h
        for h in hallazgos
        if h["regla"] in {"Import prohibido presentacion->dominio", "Import prohibido aplicacion->infraestructura"}
        and (h["archivo"], h["linea"]) not in LISTA_BLANCA_IMPORTS_PROHIBIDOS
    ]
    if violaciones_imports:
        detalle = "\n".join(
            f"- {h['archivo']}:{h['linea']} -> {h['detalle']}" for h in violaciones_imports
        )
        raise AssertionError(f"Se detectaron violaciones arquitectónicas bloqueantes:\n{detalle}")

    archivos_loc_altos = resultado["metricas"]["archivos_presentacion_loc_mayor_450"]
    if len(archivos_loc_altos) > MAX_ARCHIVOS_PRESENTACION_LOC_450:
        detalle = "\n".join(f"- {archivo}: {loc} LOC" for archivo, loc in archivos_loc_altos)
        raise AssertionError(
            "Se superó el umbral de archivos de presentación >450 LOC "
            f"(máximo {MAX_ARCHIVOS_PRESENTACION_LOC_450}):\n{detalle}"
        )

    complejos = [h for h in hallazgos if h["regla"] == "Método todo-en-uno" and h["severidad"] == "ALTO"]
    if complejos:
        detalle = "; ".join(f"{h['archivo']}:{h['linea']}" for h in complejos[:5])
        warnings.warn(
            "WARNING calidad: métodos con complejidad alta detectados (no bloqueante por transición): "
            f"{detalle}",
            stacklevel=2,
        )

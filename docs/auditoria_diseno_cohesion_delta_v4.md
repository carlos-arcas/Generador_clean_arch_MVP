# Delta auditoría diseño/cohesión (v3 → v4)

## Hallazgos cerrados

- Se mantiene en **0** el conteo de hallazgos **ALTO** activos.
- Se confirma ausencia de `except Exception` fuera de entrypoints.
- Se confirma ausencia de accesos encadenados a privados (`._x._y`).
- Se confirma ausencia de imports prohibidos entre capas críticas.

## Hallazgos persistentes

- Persisten hallazgos de complejidad **MEDIO** en validaciones y mapeos de presentación.
- Persiste un método constructor de tamaño elevado en UI (`pagina_clases.__init__`, 73 líneas).

## Nuevos hallazgos

- Aparecen nuevos hallazgos MEDIO por umbral de ramas (5–8) al endurecer el criterio v4 y ampliar cobertura de análisis por capas.
- No aparecen nuevos hallazgos ALTO.

## Tendencia estructural global

**Tendencia positiva y estable (nivel senior).**

Justificación:
- El sistema conserva ALTO en cero bajo criterios más estrictos.
- La nota global sube y queda en **9.55/10**.
- El riesgo actual es de naturaleza táctica (complejidad media localizada), no estructural.

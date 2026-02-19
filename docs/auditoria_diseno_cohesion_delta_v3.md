# Delta auditoría diseño/cohesión (v2 → v3)

## Hallazgos cerrados definitivamente

- Se elimina la condición de ALTO por complejidad extrema (>8 ramas) en métodos de auditoría/blueprints.
- No se detectan accesos privados encadenados `._x._y`.
- No aparecen importaciones prohibidas nuevas en capas (`presentacion -> dominio` o `aplicacion -> infraestructura`).
- No se detectan monolitos ALTO (>500 LOC) en `presentacion/` o `aplicacion/`.

## Hallazgos persistentes

- Persisten métodos largos (>60 líneas) en casos de uso y componentes de presentación.
- Persisten funciones con ramificación media (>5 ramas) en auditoría y validación.
- Permanece un `except Exception` fuera de entrypoint en `presentacion/trabajadores/trabajador_generacion.py`.

## Nuevos hallazgos

- No se detectan nuevos hallazgos ALTO.
- Se mantiene un ALTO histórico **justificado** en mapper de anti-corrupción (`presentacion/mappers/mapper_dominio_a_presentacion.py:5`).

## Tendencia estructural

**Mejora.**

Justificación:
- Se sostiene la reducción de deuda crítica iniciada en v2.
- Los riesgos actuales son mayoritariamente de severidad media/baja y con alcance acotado.
- La puntuación de riesgo global pasa a **8.15/10**.

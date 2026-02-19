# Guía de logging

## Ubicación
- `logs/seguimiento.log`: trazas operativas.
- `logs/crashes.log`: errores y excepciones no controladas.

## Política de errores
- UI y CLI muestran mensajes útiles al usuario (sin stacktrace).
- Los detalles técnicos se registran en `crashes.log`.

## Auditoría
El resultado consolidado se guarda en `docs/informe_auditoria.md` incluso si hay fallo en el proceso.

## Herramientas de auditoría
- Las herramientas `herramientas/auditar_diseno_cohesion_v3.py`, `v4.py` y `v5.py` también usan logging.
- No se usa `print(` para salida operativa ni para serializar resultados JSON.
- La salida de cada auditor se escribe en UTF-8 con `--salida <ruta>`.
- La ruta recomendada es `docs/` (por ejemplo `docs/auditoria_diseno_v5.json`) o una ruta explícita indicada por CLI.


# Guía de logging

## Ubicación
- `logs/seguimiento.log`: trazas operativas.
- `logs/crashes.log`: errores y excepciones no controladas.

## Política de errores
- UI y CLI muestran mensajes útiles al usuario (sin stacktrace).
- Los detalles técnicos se registran en `crashes.log`.

## Auditoría
El resultado consolidado se guarda en `docs/informe_auditoria.md` incluso si hay fallo en el proceso.

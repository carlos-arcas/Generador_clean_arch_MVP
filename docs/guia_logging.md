# Guía de logging

## Archivos de log
- `logs/seguimiento.log`: eventos de seguimiento (DEBUG/INFO y superiores).
- `logs/crashes.log`: errores y fallos críticos (ERROR/CRITICAL) con stacktrace.

## Rotación
Se utiliza `RotatingFileHandler` con tamaño máximo por archivo y backups.

## Formato
Cada registro usa el formato:

`timestamp | nivel | módulo | función | mensaje`

## Manejo de excepciones globales
Se instala `sys.excepthook` para registrar excepciones no controladas en `crashes.log`.

## Filtrado básico de secretos
Se descartan líneas que contengan palabras sensibles: `password`, `token`, `secret`.

# Plantilla de Auditoría de finalización E2E

Este documento describe el formato del informe generado por el comando:

`python -m presentacion.cli auditar-finalizacion --preset <ruta> --salida <ruta_sandbox>`

## Estructura mínima

- ID de ejecución (`AUD-...`)
- Fecha/hora
- Ruta sandbox
- Tabla de etapas con estado `PASS/FAIL/SKIP`
- Evidencias por etapa
- Conflictos detectados (total, primeras rutas y recomendación)
- Pasos de reproducción y ubicación de logs

## Etapas

1. Preparación de contexto
2. Carga de preset
3. Preflight de conflictos (rutas duplicadas)
4. Ejecución en sandbox
5. Auditoría de arquitectura
6. Smoke test (compileall/pytest)

## Recomendaciones de conflictos

Cuando hay rutas duplicadas:

- mostrar el total de rutas duplicadas
- listar entre 3 y 5 rutas
- recomendar revisar la selección de blueprints
- sugerir explícitamente posible solapamiento: CRUD de `persona` duplicado

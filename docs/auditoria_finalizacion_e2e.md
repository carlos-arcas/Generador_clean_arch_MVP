# Auditoría de finalización E2E (informe real)

- ID ejecución: `AUD-20260219-124556-3614`
- Fecha/hora ISO: `2026-02-19T12:45:56`
- Ruta sandbox absoluta: `/tmp/auditoria_finalizacion_real`
- Ruta evidencias: `docs/evidencias_finalizacion/AUD-20260219-124556-3614`
- Preset: `/tmp/preset_auditoria_real.json`

## Tabla de etapas

| Etapa | Estado | Duración ms | Resumen |
|---|---|---:|---|
| Preparación | PASS | 0 | Contexto listo |
| Carga preset | PASS | 0 | Blueprints: 2 |
| Preflight conflictos | FAIL | 10 | Error en preflight |
| Generación sandbox | SKIP | 0 | No ejecutada por fallo preflight |
| Auditoría arquitectura | SKIP | 0 | No ejecutada por fallo preflight |
| Smoke test | SKIP | 0 | No ejecutada por fallo preflight |

## Evidencias por etapa

### Preparacion
```text
Sandbox: /tmp/auditoria_finalizacion_real
Evidencias: docs/evidencias_finalizacion/AUD-20260219-124556-3614
```

### Carga Preset
```text
crud_json
crud_sqlite
```

### Preflight Conflictos
```text
El blueprint crud_json requiere al menos una clase en la especificación.
```

### Generacion Sandbox
```text
No ejecutada
```

### Auditoria Arquitectura
```text
No ejecutada
```

### Smoke Test
```text
No ejecutada
```

## Diagnóstico y recomendación

```text
Fallo inesperado detectado.
ID incidente: AUD-20260219-124556-3614
Ruta logs: docs/evidencias_finalizacion/AUD-20260219-124556-3614
```

## Comandos de reproducción

`python -m presentacion.cli auditar-finalizacion --preset /tmp/preset_auditoria_real.json --sandbox /tmp/auditoria_finalizacion_real`

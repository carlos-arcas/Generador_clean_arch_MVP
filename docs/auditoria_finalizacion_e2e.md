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
| Preflight validación entrada | FAIL | 8 | Validación de blueprint fallida |
| Preflight conflictos de rutas | SKIP | 0 | No ejecutada por fallo de validación |
| Generación sandbox | SKIP | 0 | No ejecutada por fallo de validación |
| Auditoría arquitectura | SKIP | 0 | No ejecutada por fallo de validación |
| Smoke test | SKIP | 0 | No ejecutada por fallo de validación |

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

### Preflight Validacion Entrada
```text
excepcion_tipo: ErrorValidacionDominio
excepcion_mensaje: El blueprint crud_json requiere al menos una clase en la especificación.
origen: auditar_finalizacion_proyecto.py:_preflight_validacion_entrada:257
stacktrace_recortado:
Traceback (most recent call last):
  ...
```

### Preflight Conflictos Rutas
```text
No ejecutada
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
Fallo de validación.
Etapa: Preflight validación entrada
Código: VAL-001
Tipo: VALIDACION
Mensaje: crud_json requiere al menos una clase. Blueprint culpable: crud_json. Regla: requiere al menos 1 clase. Acción: añade al menos una clase en la especificación o elimina crud_json del preset
```

## Comandos de reproducción

`python -m presentacion.cli auditar-finalizacion --preset /tmp/preset_auditoria_real.json --sandbox /tmp/auditoria_finalizacion_real`

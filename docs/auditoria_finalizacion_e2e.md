# Auditoría de finalización E2E (informe real)

- ID ejecución: `AUD-20260219-124556-3614`
- Fecha/hora ISO: `2026-02-19T12:45:56`
- Ruta sandbox absoluta: `/tmp/auditoria_finalizacion_real`
- Ruta evidencias: `docs/evidencias_finalizacion/AUD-20260219-124556-3614`
- Preset: `/tmp/preset_auditoria_real.json`

## Estado global

```text
Estado global: FAIL
Tipo fallo dominante: CONFLICTO
Código: CON-001
Etapa: Preflight conflictos de rutas
Motivo resumido: Se detectaron rutas duplicadas entre blueprints. Acción: desactiva uno de los blueprints que generan la misma ruta (p.ej. CRUD persona duplicado)
```

## Tabla de etapas

| Etapa | Estado | Duración ms | Resumen |
|---|---|---:|---|
| Preparación | PASS | 2 | Contexto listo |
| Carga preset | PASS | 1 | Blueprints: 3 |
| Preflight validación entrada | PASS | 1 | Validación de entrada OK |
| Preflight conflictos de rutas | FAIL | 5 | Rutas duplicadas detectadas |
| Generación sandbox | SKIP | 0 | No ejecutada por conflicto de rutas |
| Auditoría arquitectura | SKIP | 0 | No ejecutada por conflicto de rutas |
| Smoke test | SKIP | 0 | No ejecutada por conflicto de rutas |

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
api_fastapi
```

### Preflight Validacion Entrada
```text
Warnings declarativos:
- Incompatibilidad declarativa detectada: crud_json y crud_sqlite generan CRUD para la misma entidad. Recomendación: elige 1 CRUD.
```

### Preflight Conflictos Rutas
```text
total rutas duplicadas: 2
Ejemplos ruta -> [blueprints]:
aplicacion/persona.py -> [crud_json, crud_sqlite]
infraestructura/repositorio_persona.py -> [crud_json, crud_sqlite]

Recomendación: No selecciones más de 1 blueprint CRUD para la misma entidad.

excepcion_tipo: ErrorConflictoArchivos
excepcion_mensaje: Rutas duplicadas detectadas: 2
origen: auditar_finalizacion_proyecto.py:_preflight_conflictos_rutas:287
linea_raise: auditar_finalizacion_proyecto.py:287
stacktrace_recortado:
Traceback (most recent call last):
  File ".../aplicacion/casos_uso/auditar_finalizacion_proyecto.py", line 287, in _preflight_conflictos_rutas
    raise ErrorConflictoArchivos("Rutas duplicadas detectadas: 2")
aplicacion.errores.errores_generacion.ErrorConflictoArchivos: Rutas duplicadas detectadas: 2
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
Conflicto de generación.
Etapa: Preflight conflictos de rutas
Código: CON-001
Tipo: CONFLICTO
Mensaje: Se detectaron rutas duplicadas entre blueprints. Acción: desactiva uno de los blueprints que generan la misma ruta (p.ej. CRUD persona duplicado)
Mapa ruta -> [blueprints]:
- aplicacion/persona.py -> [crud_json, crud_sqlite]
- infraestructura/repositorio_persona.py -> [crud_json, crud_sqlite]
Detalle técnico:
excepcion_tipo: ErrorConflictoArchivos
excepcion_mensaje: Rutas duplicadas detectadas: 2
origen: auditar_finalizacion_proyecto.py:_preflight_conflictos_rutas:287
linea_raise: auditar_finalizacion_proyecto.py:287
stacktrace_recortado:
Traceback (most recent call last):
  File ".../aplicacion/casos_uso/auditar_finalizacion_proyecto.py", line 287, in _preflight_conflictos_rutas
    raise ErrorConflictoArchivos("Rutas duplicadas detectadas: 2")
aplicacion.errores.errores_generacion.ErrorConflictoArchivos: Rutas duplicadas detectadas: 2
```

## Comandos de reproducción

`python -m presentacion.cli auditar-finalizacion --preset /tmp/preset_auditoria_real.json --sandbox /tmp/auditoria_finalizacion_real`

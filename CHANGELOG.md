# Changelog

## [1.5.2] - 2026-02-18

### Corregido
- Eliminada duplicidad de módulo de auditoría.
- Unificada fuente única de auditoría.


## [1.5.1] - 2026-02-18

### Corregido
- Scripts .bat reforzados con control de errores y logging completo.


## [1.5.0] - 2026-02-18

### Añadido
- Soporte de plugins externos dinámicos.


## [1.4.0] - 2026-02-18

### Añadido
- Auditor automático post-generación


## [1.3.0] - 2026-02-18

### Añadido
- Sistema de presets reutilizables (UI + CLI).

## [1.2.0] - 2026-02-18

### Añadido
- Generación segura con validación y MANIFEST

### Corregido
- Rollback automático en fallo

## [1.1.0] - 2026-02-18

### Añadido
- Añadido: generación MVP desde wizard (base_clean_arch_v1 + crud_json_v1).

## [0.9.0] - 2026-02-18

### Modificado
- Wizard ahora usa modelo de dominio real.

## [1.0.2] - 2026-02-18

### Añadido
- Soporte de atributos dinámicos por clase en wizard.

## [1.0.1] - 2026-02-18

### Añadido
- Añadido wizard QWizard con 4 pasos (sin generación aún).
- DTO de presentación `DatosWizardProyecto` y controlador de recopilación de datos para desacoplar UI de la preparación de configuración.
- Pruebas MVP del wizard para validación de completitud, clases, persistencia y resumen.

## [1.0.0] - 2026-02-18

### Añadido
- Soporte de presets guardables/cargables en `configuracion/presets` con validación.
- CLI alternativa con comandos `generar`, `validar-preset` y `auditar`.
- Excepciones de aplicación (`ErrorValidacion`, `ErrorConflictoArchivos`, `ErrorAuditoria`, `ErrorBlueprintNoEncontrado`).
- Pruebas de regresión por snapshots de rutas de plan para combinaciones críticas de blueprints.

### Modificado
- Auditoría reforzada: siempre escribe `docs/informe_auditoria.md` y valida consistencia de `manifest.json` con hashes.
- Wizard UI con botones para guardar/cargar presets reutilizables.
- Manejo de errores en UI/CLI con mensajes de usuario en español y trazas en logging.

### Corregido
- Normalización de conflictos de plan como error de aplicación para evitar mensajes ambiguos.

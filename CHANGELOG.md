# Changelog

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

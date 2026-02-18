# Changelog

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

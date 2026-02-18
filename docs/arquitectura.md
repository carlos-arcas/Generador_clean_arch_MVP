# Arquitectura

## Capas
- **Dominio**: modelos y reglas (`EspecificacionProyecto`, `PlanGeneracion`, `PresetProyecto`).
- **Aplicación**: casos de uso (`CrearPlanDesdeBlueprints`, `CrearPlanPatchDesdeBlueprints`, `EjecutarPlan`, `AuditarProyectoGenerado`, presets).
- **Infraestructura**: repositorios de blueprints, manifest, sistema de archivos, hashes, presets en disco.
- **Presentación**: UI PySide6 y CLI por `argparse`.

## Flujo de generación
1. Captura de especificación (UI o CLI/preset).
2. Creación de plan por blueprints.
3. Ejecución de plan y generación/actualización de manifest.
4. Auditoría final (estructura, imports, logging, cobertura, consistencia manifest/hash).

## Contratos públicos congelados (v1)
- `CrearPlanDesdeBlueprints` / `CrearPlanPatchDesdeBlueprints`
- `EjecutarPlan`
- `AuditarProyectoGenerado`
- Puertos de blueprints, manifest, sistema de archivos, hash y presets.

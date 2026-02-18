# Arquitectura

## Capas
- **Dominio**: modelos y reglas (`EspecificacionProyecto`, `PlanGeneracion`, `PresetProyecto`).
- **Aplicación**: casos de uso (`CrearPlanDesdeBlueprints`, `CrearPlanPatchDesdeBlueprints`, `EjecutarPlan`, `AuditarProyectoGenerado`, presets).
- **Infraestructura**: repositorios de blueprints, manifest, sistema de archivos, hashes, presets en disco.
- **Presentación**: UI PySide6 y CLI por `argparse`.

## Presentación (wizard por páginas)
La UI de escritorio está organizada como un `QWizard` real con 4 pasos desacoplados:
1. **Datos del proyecto**: nombre, ruta destino, descripción y versión.
2. **Clases**: captura MVP de clases (sin atributos por ahora).
3. **Persistencia**: selección entre JSON y SQLite (JSON por defecto).
4. **Resumen**: consolidación read-only de la configuración capturada.

El `WizardGeneradorProyectos` delega la preparación de datos a `ControladorWizardProyecto`, que devuelve un DTO de presentación (`DatosWizardProyecto`). Este flujo mantiene la UI como orquestadora y deja preparada la integración futura con workers/casos de uso de generación.

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

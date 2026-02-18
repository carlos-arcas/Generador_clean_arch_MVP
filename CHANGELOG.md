# CHANGELOG

Todos los cambios importantes de este proyecto se documentan en este archivo.

## [0.2.0] - 2026-02-18
### Agregado
- Sistema de blueprints versionados con contrato en aplicación y repositorio en disco.
- Caso de uso para composición de `PlanGeneracion` desde múltiples blueprints.
- Manifest de generación con hashes SHA256 por archivo y metadata de ejecución.
- Caso de uso de auditoría mínima del proyecto generado.
- Nuevas pruebas unitarias para dominio, aplicación e infraestructura.

### Cambiado
- `EjecutarPlan` ahora registra archivos generados y dispara generación de `manifest.json`.
- Flujo principal de presentación actualizado a blueprints + auditoría.
- Documentación de arquitectura, decisiones técnicas y guía de pruebas actualizada.

## [0.1.0] - 2026-02-18
### Agregado
- Estructura inicial con Clean Architecture.
- Núcleo mínimo con generación y ejecución de plan de archivos.
- Configuración de logging con rotación y captura global de excepciones.
- Tests unitarios y scripts de automatización para ejecución y cobertura.

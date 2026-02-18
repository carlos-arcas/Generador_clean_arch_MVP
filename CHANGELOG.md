# CHANGELOG

Todos los cambios importantes de este proyecto se documentan en este archivo.

## [0.8.0] - 2026-02-18
### Agregado
- Modo PATCH incremental para proyectos existentes: lectura de `manifest.json`, detección de clases ya generadas y generación de plan parcial solo para clases nuevas.
- Nuevos casos de uso `CrearPlanPatchDesdeBlueprints` y `ActualizarManifestPatch`.
- Adaptadores de infraestructura `LectorManifestEnDisco` y `EscritorManifestSeguro` (escritura atómica de manifest).
- Nuevas pruebas de aplicación para escenario PATCH (`test_patch_nueva_clase.py`, `test_patch_clase_existente_error.py`, `test_actualizar_manifest_patch.py`).

### Cambiado
- `TrabajadorGeneracion` ahora detecta automáticamente modo PATCH cuando existe `manifest.json` en ruta destino.
- `EjecutarPlan` incorpora bandera `generar_manifest` para evitar sobreescribir manifest en PATCH.
- Resumen del wizard muestra clases nuevas a añadir y clases bloqueadas por existir previamente.
- Método de dominio `ManifestProyecto.obtener_clases_generadas()` para inferir entidades desde rutas del manifest.

## [0.7.0] - 2026-02-18
### Agregado
- Nuevo blueprint `crud_sqlite_v1` (`crud_sqlite@1.0.0`) con repositorios SQLite por entidad en `infraestructura/persistencia/sqlite`.
- Repositorios SQLite generados con `sqlite3` estándar, creación de tabla automática, conexión por operación y logging de CRUD/errores SQL.
- Pruebas de blueprint e intercambiabilidad para validar reemplazo JSON ↔ SQLite sin cambios en dominio/aplicación.
- Validación adicional en auditor para detectar `sqlite3` fuera de `infraestructura`.
- Selección exclusiva de persistencia (JSON o SQLite) en la página de blueprints del wizard.

### Cambiado
- Versión del generador actualizada a `0.7.0`.

## [0.6.0] - 2026-02-18
### Agregado
- Auditor avanzado de proyectos generados con validación de estructura, imports prohibidos, ciclos básicos y reglas de logging.
- Puerto `EjecutorProcesos` y adaptador `EjecutorProcesosSubprocess` para ejecutar `pytest --cov=. --cov-report=term` desde el auditor.
- Generación automática de `docs/informe_auditoria.md` dentro del proyecto generado con conclusión APROBADO/RECHAZADO.
- Nuevas pruebas unitarias para estructura, imports y cobertura mockeada del auditor.

### Cambiado
- `ResultadoAuditoria` ahora incluye `cobertura` y `resumen` además del estado general.
- Integración de UI para mostrar resumen de auditoría avanzada y registrar rechazos con detalle en logs de crashes.
- `CrearPlanProyectoBase` genera estructura base completa (capas, docs, logs y `infraestructura/logging_config.py`) para cumplir auditoría estricta.
- Versión del generador actualizada a `0.6.0`.

## [0.5.0] - 2026-02-18
### Agregado
- Nueva capa de presentación PySide6 con `VentanaPrincipal` y `WizardProyecto` de cuatro páginas (datos, clases, blueprints y resumen).
- Modelos Qt de solo lectura (`ModeloClases`, `ModeloAtributos`) para visualizar entidades de dominio sin mutarlas desde la UI.
- Ejecución en background con `QRunnable + QThreadPool` (`TrabajadorGeneracion`) y señales de progreso/finalización/error.
- Logging estructurado de inicio de generación, blueprints seleccionados, resultado de auditoría y captura global de excepciones Qt en `crashes.log`.
- Pruebas de wiring de presentación para instanciación de ventana y orquestación de casos de uso desde el trabajador.

### Cambiado
- `requirements.txt` ahora fija `PySide6` para habilitar la UI.
- Versión del generador actualizada a `0.5.0`.

## [0.4.0] - 2026-02-18
### Agregado
- Nuevo blueprint `crud_json_v1` (`crud_json@1.0.0`) para generar CRUD completo por entidad.
- Generación automática de entidad de dominio, puerto de repositorio, casos de uso CRUD, repositorio JSON y pruebas base del proyecto generado.
- Persistencia JSON por entidad en `datos/<entidad_plural>.json` con escritura atómica y asignación incremental de IDs.
- Pruebas de blueprint para validar rutas generadas, ausencia de duplicados y validación de especificación sin clases.

### Cambiado
- Versión del generador actualizada a `0.4.0`.

## [0.3.0] - 2026-02-18
### Agregado
- Modelo de dominio para constructor dinámico: `EspecificacionClase` y `EspecificacionAtributo` con reglas de validación.
- Ampliación de `EspecificacionProyecto` con gestión de clases en memoria.
- Puerto `RepositorioEspecificacionProyecto` y adaptador `RepositorioEspecificacionProyectoEnMemoria`.
- Casos de uso para agregar/eliminar/renombrar clases y agregar/editar/eliminar atributos, además de listar y obtener detalle.
- Logging en casos de uso del constructor dinámico (DEBUG/INFO/WARNING).
- Suite de pruebas de dominio y aplicación para los escenarios correctos, errores y bordes del constructor dinámico.

### Cambiado
- Versión del generador actualizada a `0.3.0`.

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

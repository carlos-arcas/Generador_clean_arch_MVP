# Arquitectura

## Capas y dependencias
Se aplica Clean Architecture estricta:

- `dominio` no depende de ninguna otra capa.
- `aplicacion` depende de `dominio` y define puertos.
- `infraestructura` implementa puertos de `aplicacion`.
- `presentacion` orquesta casos de uso y adaptadores.

Relación permitida:

`dominio <- aplicacion <- (infraestructura, presentacion)`

## Diagrama ASCII

```text
+------------------+
|   presentacion   |
+---------+--------+
          |
          v
+------------------+       +----------------------+
|    aplicacion    |<------+   infraestructura    |
| (casos y puertos)|       | (adaptadores reales) |
+---------+--------+       +----------------------+
          |
          v
+------------------+
|     dominio      |
| (entidades/reglas)|
+------------------+
```

## Flujo actualizado
1. Presentación crea una `EspecificacionProyecto`.
2. `CrearPlanDesdeBlueprints` consulta `RepositorioBlueprints`, valida blueprints y fusiona planes sin conflictos.
3. `EjecutarPlan` escribe archivos mediante `SistemaArchivos`.
4. `GenerarManifest` calcula SHA256 usando `CalculadoraHash` y persiste `manifest.json`.
5. `AuditarProyectoGenerado` verifica artefactos mínimos del proyecto.

## Sistema de blueprints
- Carpeta raíz `blueprints/` con módulos versionados por blueprint.
- Contrato común `Blueprint` (nombre, versión, validar, generar_plan).
- Implementación inicial: `base_clean_arch_v1` (`base_clean_arch@1.0.0`) que reutiliza el caso de uso de plan base.
- La composición de planes permite extender generación sin romper el núcleo.

## Manifest y auditoría
- `manifest.json` se genera siempre al ejecutar el plan con hash SHA256 por archivo.
- Se registran blueprints usados, opciones de ejecución, timestamp ISO y versión del generador.
- La auditoría mínima valida presencia de `manifest.json`, `README.md`, `VERSION`, `logs` y scripts básicos.


## Módulo constructor dinámico de clases (v0.3.0)
- **Dominio**: incorpora `EspecificacionClase` y `EspecificacionAtributo` con reglas explícitas (PascalCase, no duplicados, validaciones de nombre/tipo).
- **Aplicación**: agrega casos de uso orientados a edición incremental de modelo (`AgregarClase`, `RenombrarClase`, `AgregarAtributo`, etc.).
- **Puertos**: define `RepositorioEspecificacionProyecto` para desacoplar almacenamiento del estado.
- **Infraestructura**: implementa `RepositorioEspecificacionProyectoEnMemoria` para pruebas rápidas y sin persistencia.
- **Presentación**: no se incorpora UI en esta etapa; el módulo queda preparado para futura integración con PySide6 sin acoplar la lógica.

## Blueprint `crud_json` (v0.4.0)
- El blueprint `crud_json_v1` genera artefactos por entidad manteniendo separación por capas:
  - `dominio/entidades`: dataclasses y validaciones mínimas.
  - `aplicacion/puertos`: interfaces de repositorio CRUD.
  - `aplicacion/casos_uso/<entidad>`: crear, obtener, listar, actualizar y eliminar.
  - `infraestructura/persistencia/json`: implementación concreta del repositorio con JSON.
  - `tests/aplicacion`: pruebas CRUD base para el proyecto generado.
- La persistencia se limita a infraestructura: dominio y aplicación no conocen JSON.
- Se genera `datos/<entidad_plural>.json` por entidad y `datos/.gitkeep` para asegurar la carpeta en el proyecto.

## Capa de presentación PySide6 (v0.5.0)
- `presentacion/ventana_principal.py` aloja el wizard y no contiene reglas de negocio.
- `presentacion/wizard_proyecto.py` solo coordina casos de uso (`gestion_clases`, `CrearPlanDesdeBlueprints`, `EjecutarPlan`, `AuditarProyectoGenerado`).
- `presentacion/modelos_qt` encapsula adaptadores de lectura para tablas Qt.
- `presentacion/trabajadores/trabajador_generacion.py` ejecuta casos de uso en background usando `QRunnable`.

### Flujo background
1. El usuario configura datos + clases + blueprints en el wizard.
2. Al pulsar **Generar**, la UI construye `EspecificacionProyecto` y crea `TrabajadorGeneracion`.
3. `QThreadPool` ejecuta el worker fuera del hilo principal.
4. El worker emite señales de progreso por etapas: plan, ejecución, auditoría.
5. La UI recibe `finalizado/error`, reactiva controles y notifica resultado.

Este flujo evita bloqueo de interfaz y mantiene dependencia hacia adentro: la UI no implementa validaciones de negocio ni operaciones de IO directamente.

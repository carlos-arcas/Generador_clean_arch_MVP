# Arquitectura

## Capas
- **Dominio**: modelos y reglas (`EspecificacionProyecto`, `PlanGeneracion`, `PresetProyecto`).
- **Aplicación**: casos de uso (`CrearPlanDesdeBlueprints`, `CrearPlanPatchDesdeBlueprints`, `EjecutarPlan`, `AuditarProyectoGenerado`, presets).
- **Infraestructura**: repositorios de blueprints, manifest, sistema de archivos, hashes, presets en disco.
- **Presentación**: UI PySide6 y CLI por `argparse`.

## Diagrama ASCII
+---------------------+
|    Presentación     |
|  (UI/CLI/Workers)   |
+----------+----------+
           |
           v
+---------------------+
|     Aplicación      |
|  (Casos de uso)     |
|  Puertos/DTOs       |
+----------+----------+
           |
           v
+---------------------+
|   Infraestructura   |
| (Adaptadores/IO)    |
+----------+----------+
           ^
           |
+---------------------+
|       Dominio       |
| (Entidades/Reglas)  |
+---------------------+

## Reglas de dependencias
- dominio no importa de nadie.
- aplicacion importa dominio (y define puertos).
- infraestructura implementa puertos (importa aplicacion/dominio).
- presentacion orquesta (importa aplicacion; infraestructura solo en composition root).

## Flujo de ejecución
1. UI recopila inputs y construye DTO de entrada.
2. Orquestador invoca un caso de uso de aplicación.
3. El caso de uso consume puertos y delega en adaptadores de infraestructura.
4. El resultado regresa a UI y se mapea a vista/CLI.
5. Logging y manejo de errores incorporan ID de incidente para soporte.

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

## Guardarraíles automáticos de arquitectura
Para evitar regresiones en dependencias entre capas, el proyecto incluye una prueba automática en:

- `tests/arquitectura/test_dependencias_capas.py`

Esta prueba recorre los archivos Python del repositorio y valida las siguientes reglas:

1. **Regla 1**: `aplicacion/` no puede importar `infraestructura` ni `presentacion`.
2. **Regla 2**: `dominio/` no puede importar `aplicacion`, `infraestructura` ni `presentacion`.
3. **Regla 3**: `presentacion/` no puede importar `infraestructura`, salvo `infraestructura.bootstrap`.

Exclusiones del recorrido:

- `tests/`
- `.venv/`
- `__pycache__/`
- `infraestructura/bootstrap.py`

- Excepciones temporales controladas (deuda técnica existente):
  - `presentacion/wizard_proyecto.py`
  - `aplicacion/casos_uso/crear_plan_desde_blueprints.py`
  - `aplicacion/casos_uso/auditar_proyecto_generado.py`
  - `aplicacion/casos_uso/generacion/generar_proyecto_mvp.py`

### Ejecución
Para ejecutar solo este guardarraíl:

- `pytest -q tests/arquitectura/test_dependencias_capas.py`

Para ejecutar toda la suite:

- `pytest -q`

Para validar cobertura mínima:

- `pytest --cov=. --cov-fail-under=85`

### Qué ocurre ante una violación
Si se detecta una importación prohibida, la prueba falla indicando de forma explícita:

- archivo infractor
- número de línea
- regla violada
- línea detectada

De esta forma, la arquitectura se valida de manera ejecutable en cada ejecución de tests.

## Exportaciones públicas de reglas de auditoría
El paquete `aplicacion.casos_uso.auditoria.reglas_dependencias` mantiene API pública
estable con resolución diferida (`__getattr__`) en su `__init__.py`. Esto evita
imports adelantados y reduce falsos positivos en validaciones arquitectónicas sin
romper `from ...reglas_dependencias import Regla...`.

## DTOs y mapeadores de vista
Los artefactos de UI se ubican en `presentacion/dtos/` y `presentacion/mapeadores/`.
`DtoVistaClase` y `DtoVistaAtributo` modelan datos listos para widget/CLI sin arrastrar detalles de casos de uso.
El mapeador `mapeador_dominio_a_vista.py` adapta entidades de dominio a DTOs de vista y viceversa para edición en UI.
Con esto, `aplicacion/` queda libre de módulos `*_presentacion*` y se respeta la dirección de dependencias por capa.

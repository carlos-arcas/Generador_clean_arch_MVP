# Auditoría de diseño y cohesión

## Resumen ejecutivo

El diseño actual es **funcional pero con señales claras de deuda estructural**: hay clases que concentran UI + orquestación + acceso a servicios, un módulo de dominio sobredimensionado y varios puntos con acoplamiento implícito. La arquitectura declarada (Clean Architecture) está parcialmente respetada, pero en la práctica aparecen atajos (acceso a atributos privados, mutación cruzada, excepciones amplias) que erosionan SRP, cohesión y mantenibilidad.

## Top 10 problemas priorizados

1. **`WizardGeneradorProyectos` concentra demasiadas responsabilidades (SRP roto).**
   - Mezcla: inicialización de UI, resolución de dependencias, orquestación de casos de uso, persistencia de credenciales, guardado/carga de presets, control de estado asíncrono y mensajería al usuario. (`presentacion/wizard/wizard_generador.py`).
2. **Método `_al_finalizar` con demasiadas ramas y responsabilidades.**
   - Valida datos, intenta guardar credenciales, maneja errores de UI, construye entrada de caso de uso y dispara worker asíncrono en un mismo bloque.
3. **Acoplamiento alto por acceso a detalle interno (`_almacen`) de otro caso de uso.**
   - `_cargar_preset_desde_ui` accede a `self._cargar_preset._almacen.listar()`, rompiendo encapsulación.
4. **`dominio/modelos.py` es un archivo “megafichero” de baja cohesión.**
   - Conviven modelos de especificación, planificación de archivos y manifest en un único módulo.
5. **`GenerarProyectoMvp.ejecutar` es una “orquestación monolítica”.**
   - Hace validación, normalización de blueprints, creación de estructura, ejecución de plan, generación de manifest, auditoría y rollback en un solo método.
6. **Bloque `except Exception` amplio en generación MVP.**
   - Captura errores heterogéneos y los transforma en resultado de salida, ocultando fronteras de fallo y dificultando diagnóstico semántico.
7. **Mutación de entidad de entrada desde la capa de aplicación.**
   - `GenerarProyectoMvp` reasigna `nombre_proyecto` y `ruta_destino` en la especificación recibida, debilitando invariantes y trazabilidad.
8. **`AuditarProyectoGenerado` mezcla políticas heterogéneas y mecanismo de ejecución externa.**
   - Valida estructura, archivos, manifest, dependencias por regex y también ejecuta subprocess de `pytest`.
9. **`bootstrap/composition_root.py` demasiado acoplado y verboso.**
   - Contiene wiring completo de infraestructura + aplicación y además resuelve catálogo para UI en el mismo módulo.
10. **`presentacion/cli/__main__.py` mezcla parsing CLI, reglas de modo patch, mutación de preset y ejecución de casos de uso.**
    - Cohesión media-baja y crecimiento difícil al agregar comandos.

## Refactors sugeridos

- Extraer de `WizardGeneradorProyectos` servicios específicos:
  - `ServicioCredencialesWizard` (persistencia segura)
  - `ServicioPresetsWizard` (guardar/cargar/listar)
  - `OrquestadorGeneracionWizard` (construcción de entrada y dispatch del worker)
- Dividir `_al_finalizar` en pasos puros y testables:
  1) `validar_y_construir_especificacion`
  2) `persistir_credenciales_si_aplica`
  3) `iniciar_generacion_async`
- Eliminar acceso a `_almacen` exponiendo `listar_presets()` en el caso de uso `CargarPresetProyecto`.
- Particionar `dominio/modelos.py` en módulos cohesionados:
  - `dominio/especificacion.py`
  - `dominio/plan_generacion.py`
  - `dominio/manifest.py`
- En `GenerarProyectoMvp`, introducir colaboradores:
  - `NormalizadorBlueprints`
  - `PreparadorEstructuraProyecto`
  - `ManejadorRollbackGeneracion`
- Reemplazar `except Exception` genérico por excepciones de negocio/infraestructura mapeadas explícitamente.
- Hacer inmutable `EspecificacionProyecto` o usar un método de copia controlada (`with_ruta_destino`, `with_nombre_proyecto`).
- Dividir `AuditarProyectoGenerado` en reglas pluggables (`ReglaEstructura`, `ReglaManifest`, `ReglaDependencias`, `ReglaPruebasOpcionales`).
- Simplificar `composition_root` en fábricas por contexto (`crear_contenedor_cli`, `crear_contenedor_gui`).
- En CLI, separar capa de comandos (`handlers`) de reglas de negocio de selección de modo (`ModoGeneracionResolver`).

## Riesgos si no se corrige

- Incremento de costo de cambio y regresiones al tocar wizard o generación MVP.
- Mayor fragilidad ante nuevas funcionalidades (más ramas condicionales en clases ya saturadas).
- Acoplamiento accidental que limita testeo unitario y reutilización.
- Erosión progresiva de límites de Clean Architecture por atajos de encapsulación.
- Diagnóstico de errores más caro por manejo de excepciones demasiado general.

## Nivel de diseño actual

**6/10.**

Base aceptable y con intención arquitectónica correcta, pero con varios puntos críticos de SRP, cohesión y acoplamiento que deben abordarse antes de escalar el sistema.

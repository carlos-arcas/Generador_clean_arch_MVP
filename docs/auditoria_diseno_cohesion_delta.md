# Delta auditoría diseño/cohesión (v1 -> v2)

## Hallazgos corregidos

- **`dominio/modelos.py` megamódulo**: **CORREGIDO**. El archivo quedó mínimo y la separación por módulos (`especificacion`, `plan_generacion`, `manifest`) está aplicada.
- **`GenerarProyectoMvp.ejecutar` gigante**: **MEJORADO/CASI CORREGIDO**. El método actual (48 líneas, baja ramificación) ya no aparece como crítico.
- **`bootstrap/composition_root.py` acoplado y verboso**: **CORREGIDO**. El archivo actual es compacto (31 LOC).
- **CLI `_ejecutar_generar` monolítico**: **CORREGIDO**. Se observa separación en funciones (`_resolver_preset`, `_construir_entrada`, `_ejecutar_generacion`, `_renderizar_resultado`).

## Hallazgos persistentes

- **wizard SRP**: **PERSISTE (MEDIO)** en `presentacion/wizard/wizard_generador.py`.
- **`_al_finalizar` todo-en-uno**: **MEJORADO** (25 líneas, 2 ramas), pero el wizard global sigue concentrando responsabilidades.
- **acoplamiento a `_almacen` privado**: **PERSISTE (ALTO)** en `presentacion/wizard/wizard_generador.py:203`.
- **`except Exception` amplio**: **PERSISTE (MEDIO)** en wizard/orquestador e infraestructura de credenciales.
- **auditoría multipropósito**: **PERSISTE (ALTO/MEDIO)** en `aplicacion/casos_uso/auditar_proyecto_generado.py` (método `_validar_imports` de complejidad alta).

## Nuevos hallazgos

1. **ALTO** — Métodos de blueprints con complejidad alta:
   - `blueprints/crud_json_v1/blueprint.py:436`
   - `blueprints/crud_sqlite_v1/blueprint.py:80`
2. **ALTO** — Imports sospechosos `presentacion -> dominio`:
   - `presentacion/modelos_qt/modelo_atributos.py:7`
   - `presentacion/modelos_qt/modelo_clases.py:7`
3. **MEDIO** — Archivos con muchas clases (potencial baja cohesión):
   - `aplicacion/errores.py`
   - `aplicacion/casos_uso/gestion_clases.py`
   - `aplicacion/casos_uso/generacion/pasos/errores_pipeline.py`

## Riesgo global (antes vs después)

- **Antes (v1): 6/10, riesgo alto-medio**.
- **Después (v2): 7/10, riesgo medio**.

> Nota: baja el riesgo estructural en puntos históricos críticos (módulos gigantes/orquestadores monolíticos), pero aún hay deuda técnica en acoplamiento de capas y complejidad de validaciones/generación de plantillas.

## Acciones priorizadas recomendadas

1. **Prioridad 1**: romper acoplamientos de capa (`presentacion -> dominio`) con DTOs/puertos de presentación.
2. **Prioridad 1**: eliminar acceso a privado `._almacen` exponiendo operación pública en caso de uso.
3. **Prioridad 2**: refactor de `AuditarProyectoGenerado._validar_imports` a reglas desacopladas.
4. **Prioridad 2**: trocear métodos largos de blueprints para reducir complejidad accidental.
5. **Prioridad 3**: endurecer política de excepciones (evitar `except Exception` salvo borde explícito).

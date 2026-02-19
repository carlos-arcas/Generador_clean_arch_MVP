# Auditoría de diseño y cohesión v2

## 1) Resumen ejecutivo

La re-auditoría confirma una mejora clara respecto a la versión anterior: se redujeron los focos de monolitismo en `dominio/`, `bootstrap/`, CLI y en la orquestación principal de generación. Persisten, no obstante, riesgos de acoplamiento y complejidad en puntos concretos. Los hallazgos críticos actuales se concentran en: imports de `presentacion` hacia `dominio`, acceso a privados encadenados y métodos de alta complejidad en auditoría y blueprints. No se detectaron archivos de `presentacion/` por encima de 450 LOC. El riesgo global baja de **alto-medio** a **medio**.

## 2) Top 10 problemas de diseño (priorizados)

1. **ALTO** — Método todo-en-uno en `AuditarProyectoGenerado._validar_imports` (`aplicacion/casos_uso/auditar_proyecto_generado.py:143`).
2. **ALTO** — Método todo-en-uno en `CrudJsonBlueprint._contenido_test_crud` (`blueprints/crud_json_v1/blueprint.py:436`).
3. **ALTO** — Método todo-en-uno en `CrudSqliteBlueprint._contenido_repositorio_sqlite` (`blueprints/crud_sqlite_v1/blueprint.py:80`).
4. **ALTO** — Import sospechoso `presentacion -> dominio` en `presentacion/modelos_qt/modelo_atributos.py:7`.
5. **ALTO** — Import sospechoso `presentacion -> dominio` en `presentacion/modelos_qt/modelo_clases.py:7`.
6. **MEDIO** — `aplicacion/casos_uso/auditar_proyecto_generado.py` concentra múltiples clases (`clases=4`).
7. **MEDIO** — `AuditarProyectoGenerado.ejecutar` mantiene tamaño elevado (61 líneas) en `aplicacion/casos_uso/auditar_proyecto_generado.py:73`.
8. **MEDIO** — `WizardGeneradorProyectos` conserva señales SRP (múltiples métodos públicos y responsabilidades de UI + orquestación) en `presentacion/wizard/wizard_generador.py`.
9. **MEDIO** — Capturas amplias `except Exception` en flujo de wizard/orquestadores/infra (`presentacion/wizard/wizard_generador.py`, `presentacion/wizard/orquestadores/orquestador_finalizacion_wizard.py`, `infraestructura/seguridad/fabrica_repositorio_credenciales.py`).
10. **MEDIO** — Acceso privado encadenado `self._cargar_preset._almacen` en `presentacion/wizard/wizard_generador.py:203`.

## 3) Hallazgos por categoría

### SRP

- `WizardGeneradorProyectos` sigue actuando como punto de agregación de responsabilidades de UI y coordinación.
- `aplicacion/casos_uso/auditar_proyecto_generado.py` mantiene mezcla de clases/reglas en un solo archivo.

### Cohesión

- Sin monolitos >350 LOC en `presentacion/` o `aplicacion/`.
- Se detectan archivos con muchas clases en `aplicacion/errores.py`, `aplicacion/casos_uso/gestion_clases.py` y `aplicacion/casos_uso/generacion/pasos/errores_pipeline.py`.

### Acoplamiento

- Persisten imports sospechosos de `presentacion` hacia `dominio` en modelos Qt.
- Persiste acceso encadenado a privado (`._x._y`) en wizard.
- No se detectaron imports prohibidos nuevos de `aplicacion` hacia `infraestructura`.

### Complejidad

- Picos de complejidad en `AuditarProyectoGenerado._validar_imports` y en generadores de contenido de blueprints.
- Persisten varios `except Exception` amplios como mecanismo defensivo transversal.

## 4) Recomendaciones concretas (siguientes refactors)

1. Extraer `validador_imports` desde `AuditarProyectoGenerado` a una regla/pluggable dedicada.
2. Dividir los métodos de construcción de plantillas extensas en blueprints en bloques por responsabilidad (repositorio, pruebas, utilidades).
3. Introducir puerto/DTO específico para los modelos Qt y evitar dependencia directa de `dominio` desde `presentacion`.
4. Eliminar `self._cargar_preset._almacen.listar()` exponiendo `listar_presets()` en caso de uso.
5. Sustituir `except Exception` por excepciones semánticas (infraestructura, validación, IO) y mapping explícito.
6. Continuar particionando `WizardGeneradorProyectos` hacia servicios/orquestadores especializados.

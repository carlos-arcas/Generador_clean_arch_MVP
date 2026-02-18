# Auditoría de calidad real de testing

## 1) Resumen ejecutivo

La suite tiene una base sólida en cantidad y separación por capas, pero con una brecha clara entre **cobertura numérica** y **poder de detección de regresiones**.

- La cobertura global reportada es **89%** y supera el umbral objetivo del 85%.
- Sin embargo, hay señales de calidad desigual: asserts débiles en algunos tests, pruebas de arquitectura basadas en búsqueda de strings y zonas críticas de seguridad/plataforma prácticamente sin validación real.
- En UI/Qt hay una dependencia fuerte de `importorskip`, por lo que parte de la superficie de presentación puede no ejercitarse en entornos CI no preparados.
- En seguridad de credenciales, el adaptador de Windows y la fábrica de selección por plataforma están poco o nada probados.

## 2) Nivel real del testing (0–10)

**7/10**

Justificación breve:
- **+** Buen volumen (132 tests), mezcla de unitarias, integración, regresión por snapshot y tests de arquitectura.
- **+** Existe prueba E2E útil del flujo principal de generación MVP.
- **−** Cobertura heterogénea en módulos críticos de seguridad/plataforma.
- **−** Algunos tests validan presencia/forma, pero no semántica ni invariantes profundas.
- **−** Parte de pruebas de presentación depende del entorno (saltables).

## 3) Top 10 debilidades reales

1. **Asserts triviales en composition root** (`is not None`) validan existencia de objetos, no comportamiento ni contrato.
2. **Asserts de arranque UI poco profundos** (ej. "no crashea" + cantidad de páginas), sin validar interacciones de negocio.
3. **Tests de arquitectura por inspección de texto** (`"infraestructura." not in contenido`) son frágiles y fáciles de falsear.
4. **Cobertura muy baja en credenciales Windows (16%)** en un componente de seguridad sensible.
5. **Sin tests directos para la fábrica de repositorio de credenciales** y su fallback por plataforma/errores.
6. **Uso de dobles simples sin verificar payload completo** (p.ej., manifest generado: se valida llamada, no contenido contractual completo).
7. **Flujos negativos de puertos parcialmente cubiertos**: faltan contratos sistemáticos de errores para adaptadores externos.
8. **Dependencia de entorno en tests Qt**: múltiples pruebas pueden saltarse completas si PySide6 no está disponible.
9. **Falta de tests de propiedades/invariantes fuertes** en módulos de transformación compleja (blueprints con ramas sin cubrir).
10. **Ausencia de gate de mutación o calidad de asserts**: cobertura alta puede esconder tests que ejecutan más que validan.

## 4) Zonas críticas que requieren más pruebas

1. **Seguridad / credenciales**
   - `infraestructura/seguridad/repositorio_credenciales_windows.py`
   - `infraestructura/seguridad/fabrica_repositorio_credenciales.py`

2. **Contratos de generación de manifest y puertos**
   - Verificar shape exacto de argumentos y persistencia final en todos los caminos (éxito/errores parciales).

3. **Blueprints con ramas no cubiertas**
   - Especialmente `blueprints/crud_json_v1/blueprint.py` y exportadores donde hay líneas sin cubrir.

4. **Presentación Qt en CI estable**
   - Asegurar que las pruebas hoy saltables se ejecuten siempre en pipeline reproducible.

5. **Flujos de error encadenados del caso de uso principal**
   - Fallos intermedios después de crear directorios pero antes de finalizar auditoría/manifest.

## 5) Recomendaciones técnicas concretas

1. **Reemplazar asserts triviales por contratos observables**
   - En lugar de `is not None`, validar interfaz mínima esperada y efectos.

2. **Añadir tests de contrato para puertos/adaptadores**
   - Definir una batería reusable para cada implementación (`SistemaArchivos`, repositorios, manifest, credenciales).

3. **Blindar seguridad multiplataforma**
   - Añadir tests con `monkeypatch` de `sys.platform` + dobles de `ctypes` para ruta Windows y fallback.

4. **Fortalecer pruebas de errores**
   - Casos explícitos para excepción en `auditor`, excepción en `ejecutar_plan`, y consistencia de rollback.

5. **Verificar payloads completos en dobles**
   - Validar contenido de kwargs en llamadas a generador de manifest (blueprints/version/opciones/rutas).

6. **Reducir fragilidad de tests de arquitectura**
   - Cambiar checks por strings a análisis de imports vía AST.

7. **Agregar mutation testing (pilot)**
   - Ejecutar en capa dominio y casos de uso críticos para medir fuerza real de asserts.

8. **Convertir skips de Qt en jobs dedicados de CI**
   - Pipeline con dependencia PySide6 para evitar "falsos verdes" por tests omitidos.

9. **Matriz mínima de regresión por combinaciones de blueprints**
   - No solo snapshots de rutas; validar archivos clave e invariantes de contenido.

10. **Configurar cobertura focalizada por riesgo**
   - Mantener umbral global, pero exigir mínimos por paquete crítico (seguridad/aplicación).

## 6) ¿Listo para refactors grandes?

**Parcialmente listo (con riesgo moderado).**

- El núcleo funcional principal está razonablemente protegido por unitarias + integración.
- Pero hay riesgo significativo en cambios de seguridad/plataforma y en zonas cubiertas con asserts débiles.
- Antes de un refactor grande, conviene primero endurecer contratos de puertos, seguridad y pruebas de errores para bajar probabilidad de regresiones silenciosas.

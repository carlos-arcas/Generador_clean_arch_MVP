# PROMPT AUDITOR 11 — Auditoría de Seguridad Técnica Real

## 1) Resumen ejecutivo

La base tiene **intención de seguridad** (filtro de secretos en logs, `__repr__` enmascarado para credenciales y uso de Windows Credential Manager cuando está disponible), pero presenta brechas relevantes en controles de escritura de archivos, validación de rutas y confianza en extensibilidad por plugins. El vector dominante es **escritura arbitraria en filesystem** por rutas no confinadas (desde planes/plantillas/presets), con posibilidad de sobrescritura fuera del proyecto objetivo.

## 2) Nivel de seguridad actual (0–10)

**5.8 / 10**

- Fortalezas: manejo nativo de credenciales en Windows, sanitización parcial de secretos en logs, `subprocess.run` sin `shell=True`.
- Debilidades: falta de *path confinement* estricto, validación incompleta de identificadores de código generado, plugins sin autenticidad/integridad, y exposición de metadatos internos por logging de excepciones.

## 3) Top 10 vulnerabilidades reales

1. **Path traversal en escritura de archivos del plan de generación (Alta)**
   - `EjecutarPlan` concatena `ruta_destino` + `archivo.ruta_relativa` y escribe sin validar que el resultado permanezca dentro de `ruta_destino`.
   - Riesgo: un blueprint/plugin malicioso puede incluir rutas como `../../.ssh/authorized_keys`.

2. **Escritura atómica sin política de confinamiento (Alta)**
   - `SistemaArchivosReal.escribir_texto_atomico` crea y reemplaza archivos en la ruta recibida sin controles de raíz permitida.
   - Riesgo: sobreescritura de archivos críticos del sistema/usuario si ruta llega manipulada.

3. **Carga de presets desde rutas arbitrarias (Alta)**
   - `_resolver_ruta_preset` permite rutas absolutas o relativas con parent (`../`) y no restringe al directorio seguro de presets.
   - Riesgo: lectura de archivos JSON fuera de `configuracion/presets` y abuso de datos no confiables.

4. **Guardado de presets en destino arbitrario (Alta)**
   - `guardar(..., ruta=...)` acepta cualquier ruta; no hay validación de alcance ni denylist de rutas sensibles.
   - Riesgo: sobrescritura de cualquier `.json` alcanzable por permisos del proceso.

5. **Plugins externos sin autenticación/firmado (Alta)**
   - `DescubridorPlugins` acepta cualquier carpeta local con `blueprint.json`; no hay firma, hash, allowlist de origen ni control de permisos.
   - Riesgo: inyección de contenido malicioso en archivos generados.

6. **Posible exfiltración por symlinks en templates de plugins (Media-Alta)**
   - El cargador de plugin recorre `templates` y hace `read_text` de cada archivo encontrado; no valida symlinks ni destino real.
   - Riesgo: incluir contenido de archivos externos (si hay symlink) dentro de archivos del proyecto generado.

7. **Validación insuficiente de nombres de atributos/tipos para generación de código (Media)**
   - `EspecificacionAtributo.nombre` solo bloquea vacío/espacios, no valida identificadores Python seguros.
   - Riesgo: ruptura del código generado y posibilidad de inyección sintáctica en plantillas que interpolan campos.

8. **No hay política de permisos/propietario antes de operar sobre rutas (Media)**
   - No se comprueban owner/permisos de rutas destino antes de escribir (`mkdir`, `replace`).
   - Riesgo: escritura en rutas compartidas o montajes inseguros con archivos sensibles.

9. **Logging de excepciones puede filtrar información interna (Media)**
   - `LOGGER.exception` y `exc_info` global registran stack traces completos; el filtro solo cubre patrones simples de secretos.
   - Riesgo: exposición de rutas internas, nombres de módulos y mensajes con datos sensibles no matcheados por regex.

10. **Fallback de credenciales a memoria no endurecido (Media-Baja)**
   - Si falla backend seguro, se usa almacenamiento en memoria sin TTL, sin borrado seguro de secreto y sin hardening adicional.
   - Riesgo: extracción en memoria de proceso (escenario local, debugging/memory dump).

## 4) Riesgo operativo

- **Probabilidad de incidente:** Media-Alta (sobre todo en entornos donde se aceptan plugins/presets externos).
- **Impacto potencial:** Alto (sobrescritura de archivos fuera del proyecto, corrupción de configuración local, fuga de info interna).
- **Áreas más expuestas:** ejecución de planes de generación, persistencia/carga de presets y ecosistema de plugins.

## 5) Recomendaciones concretas por prioridad

### Prioridad P0 (inmediata)

1. **Confinar rutas de escritura y lectura**
   - Resolver rutas con `Path.resolve()` y verificar `destino_resuelto.is_relative_to(base_resuelta)` (o equivalente con comparación de prefijos robusta).
   - Rechazar rutas absolutas y segmentos `..` en `ArchivoGenerado.ruta_relativa`.

2. **Blindar presets**
   - Forzar `cargar`/`guardar` exclusivamente bajo `configuracion/presets` salvo modo admin explícito.
   - Validar nombre de preset con regex segura (`^[a-zA-Z0-9_-]+$`).

3. **Modelo de confianza para plugins**
   - Activar allowlist de plugins + checksum SHA256 por plugin.
   - Rechazar symlinks en `templates` y validar que cada archivo resuelto permanezca bajo `templates`.

### Prioridad P1 (corto plazo)

4. **Validar identificadores de código generado**
   - `EspecificacionAtributo.nombre`: regex de identificador Python y denylist de palabras reservadas (`keyword.kwlist`).
   - `tipo`: allowlist o parser estricto para tipos admitidos.

5. **Reducir exposición en logs**
   - Añadir redacción estructurada de secretos en formato JSON/URL (`Authorization`, `Bearer`, `client_secret`, etc.).
   - Evitar stack trace completo en logs de producción; mover detalles a canal restringido.

6. **Controles de permisos previos a escritura**
   - Verificar que destino no sea symlink, que exista permiso esperado y que pertenezca al usuario/proyecto objetivo.

### Prioridad P2 (mediano plazo)

7. **Seguridad de credenciales en fallback**
   - TTL y borrado explícito de credenciales en memoria al finalizar operación.
   - Señalización visible de “modo no seguro” cuando no hay backend protegido.

8. **Auditoría de seguridad automática**
   - Añadir checks de rutas inseguras, symlinks y reglas anti-traversal en CI.

## 6) ¿Está preparado para entorno empresarial?

**No, todavía no para un entorno empresarial con requisitos de seguridad estrictos.**

Puede entrar en un entorno controlado/interno con bajo riesgo, pero antes de producción corporativa necesita al menos: confinamiento estricto de rutas, cadena de confianza para plugins y endurecimiento de presets/logging.

## Evidencia técnica (código revisado)

- Escritura de archivos sin confinamiento de ruta en ejecución de plan.
- Implementación de filesystem sin validación de raíz.
- Resolución de presets permitiendo rutas arbitrarias.
- Descubrimiento/carga de plugins sin autenticidad ni control de symlinks.
- Sanitización de logs basada en regex limitada.
- Uso de `subprocess.run` sin `shell=True` (punto positivo).
- Gestión de credenciales segura en Windows + fallback en memoria.

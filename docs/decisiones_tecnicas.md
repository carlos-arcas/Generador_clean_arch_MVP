# Decisiones técnicas

## Sistema de plugins mediante blueprints
Se introduce un contrato `Blueprint` con `RepositorioBlueprints` para desacoplar la construcción del plan de generación del flujo principal. Esto permite evolución incremental: se pueden sumar blueprints nuevos sin alterar los casos de uso centrales.

## Plan compuesto y validación de conflictos
`PlanGeneracion` ahora permite `fusionar` y validar conflictos de rutas. Esta decisión evita sobreescrituras silenciosas y convierte errores de diseño de blueprint en fallos explícitos de dominio.

## Manifest con hashes SHA256
Se agrega `manifest.json` con metadata de trazabilidad (versión del generador, blueprints usados, opciones, timestamp y hashes). Motivos:
- auditoría posterior,
- detección de cambios de contenido,
- soporte futuro para verificación de integridad.

## Auditoría mínima automatizada
`AuditarProyectoGenerado` valida artefactos obligatorios en disco tras la generación. Con esto el sistema puede dar una señal binaria rápida (`valido`) más lista de errores accionables, sin mezclar lógica de UI ni `print`.

## Uso de puertos para IO y hashing
La escritura de archivos (`SistemaArchivos`) y el hash (`CalculadoraHash`) se modelan como puertos para mantener testabilidad y cumplimiento de dependencia hacia adentro.


## IDs internos con UUID4 en clases y atributos
Se adopta `id_interno` con UUID4 para `EspecificacionClase` y `EspecificacionAtributo` para asegurar identidad estable independiente del nombre visible. Esto permite renombrar elementos sin perder referencias y simplifica operaciones de edición/eliminación.

## Separación dominio/aplicación en el constructor dinámico
Las reglas de consistencia (nombres válidos, duplicados, PascalCase, existencia) viven en dominio. Los casos de uso de aplicación solo orquestan recuperación/guardado y logging. Esta separación mantiene el núcleo testeable sin UI y evita lógica duplicada.

## Repositorio en memoria como primera implementación
Se implementa `RepositorioEspecificacionProyectoEnMemoria` para habilitar pruebas unitarias deterministas sin IO de disco ni dependencias externas. Es una base para futuras implementaciones persistentes manteniendo el mismo puerto de aplicación.

## Persistencia JSON como etapa intermedia
Se incorpora un blueprint de CRUD sobre archivos JSON para entregar una persistencia útil sin sumar dependencias externas. Esto permite validar el flujo de extremo a extremo antes de introducir SQLite u otros motores.

## ID incremental gestionado en repositorio
La asignación de `id` ocurre dentro del repositorio JSON al momento de `crear`, calculando `max(id)+1`. Con esto se evita que dominio/aplicación dependan de detalles de almacenamiento y se centraliza la política de identidad en infraestructura.

## Escritura atómica con archivo temporal + replace
Los repositorios JSON escriben usando `tempfile.mkstemp` y `Path.replace` para minimizar riesgo de corrupción ante fallos de escritura. Esta estrategia mantiene consistencia de los archivos de datos con mecanismos del estándar de Python.


## `QRunnable + QThreadPool` para generación en segundo plano (v0.5.0)
Se adopta `QRunnable` en lugar de `QThread` dedicado porque la generación es una tarea discreta (job puntual) sin ciclo de vida largo. `QThreadPool` simplifica reutilización de hilos, reduce overhead de creación/destrucción y evita gestionar manualmente señales de parada. La UI mantiene una única responsabilidad: reaccionar a señales de progreso/finalización/error.

## Separación modelos Qt / dominio
Los `QAbstractTableModel` (`ModeloClases`, `ModeloAtributos`) operan en modo lectura sobre entidades de dominio (`EspecificacionClase`, `EspecificacionAtributo`). Las mutaciones ocurren exclusivamente vía casos de uso (`AgregarClase`, `EditarAtributo`, etc.). Esta decisión evita duplicar reglas en widgets y preserva Clean Architecture: presentación adapta datos; dominio/aplicación gobiernan invariantes.

## Auditoría de imports por análisis estático simple (v0.6.0)
Se implementa análisis estático básico con lectura de archivos `.py` y regex (`import X`, `from X import ...`) sin dependencias externas. Motivos:
- mantener el generador liviano,
- evitar acoplarse a parsers complejos,
- cubrir reglas de arquitectura objetivo de forma determinista y testeable.

## Ejecución externa de pytest+coverage desde auditor
La cobertura del proyecto generado se valida ejecutando `pytest --cov=. --cov-report=term` dentro de la carpeta generada. Motivos:
- verificar calidad real del artefacto generado (no solo del generador),
- detectar fallos de wiring entre archivos y tests del proyecto destino,
- emitir un resultado de auditoría accionable con umbral explícito (>=85%).

## Puerto `EjecutorProcesos` para comandos externos
La ejecución de procesos se modela como puerto (`EjecutorProcesos`) con implementación concreta en infraestructura (`EjecutorProcesosSubprocess`). Motivos:
- preservar inversión de dependencias en Clean Architecture,
- permitir pruebas unitarias del auditor con mocks de cobertura 90%/70% sin lanzar `pytest` real,
- aislar detalles de `subprocess` fuera de la capa de aplicación.


## Persistencia SQLite sin ORM externo (v0.7.0)
Se adopta `sqlite3` del estándar de Python para el blueprint `crud_sqlite` en lugar de un ORM. Motivos:
- cero dependencias adicionales en el generador y en proyectos generados,
- control explícito sobre SQL emitido para auditoría y trazabilidad,
- alineación con el objetivo didáctico de Clean Architecture (puertos + adaptadores concretos).

## Conexión SQLite por operación
Los repositorios SQLite abren conexión en cada operación CRUD usando context manager (`with sqlite3.connect(...)`). Motivos:
- simplicidad operacional y menor estado compartido,
- cierre determinista incluso ante excepciones,
- menor riesgo de fugas de conexión en artefactos generados.

## Intercambiabilidad real por puertos de aplicación
JSON y SQLite implementan el mismo puerto `Repositorio<Entidad>`. Los casos de uso y entidades se conservan idénticos entre blueprints de persistencia. Esto permite cambiar de adaptador sin modificar dominio ni aplicación, cumpliendo inversión de dependencias de Clean Architecture.

## No sobrescritura por defecto en PATCH (v0.8.0)
Se adopta política estricta de no sobrescritura: si una clase ya existe en manifest o algún archivo objetivo ya existe en disco, la operación PATCH se aborta de forma controlada. Motivos:
- proteger proyectos ya generados de cambios destructivos,
- evitar divergencia silenciosa entre código real y manifest,
- mantener trazabilidad de cambios incrementales.

## Actualización incremental de manifest
En PATCH no se regenera el manifest completo. Se anexan exclusivamente nuevas entradas (`ruta_relativa + hash_sha256`) y se conserva intacto el histórico previo. Motivos:
- minimizar riesgo de corrupción de metadata existente,
- conservar hashes originales como evidencia de integridad,
- simplificar auditoría de cambios incrementales.

## Escritura atómica obligatoria de manifest
La persistencia de `manifest.json` usa archivo temporal + replace atómico. Motivos:
- evitar archivos truncados ante fallos intermedios,
- asegurar estado consistente incluso con cierres inesperados,
- mantener confiabilidad del punto de control de PATCH.


## Exportación tabular por formato con puertos en aplicación (v0.9.0)
Se decide modelar exportación como puertos de aplicación por formato (`CSV`, `Excel`, `PDF`) y casos de uso de informe por entidad. Motivos:
- mantener dominio totalmente aislado de infraestructura,
- permitir reemplazar librerías de exportación sin tocar casos de uso,
- evitar acoplar la lógica de obtención de datos al mecanismo de salida.

## PDF básico sin maquetación avanzada
Se adopta un exportador PDF funcional mínimo (título, encabezados y filas con salto de página automático). Motivos:
- cumplir necesidad operativa de exportar reportes sin introducir complejidad de diseño visual,
- reducir superficie de errores y mantenimiento,
- conservar consistencia con enfoque MVP del generador.

## Dependencias explícitas para informes
Se incorporan `openpyxl` y `reportlab` con versión fija en `requirements.txt` del generador y en plantillas base del proyecto generado. Motivos:
- evitar diferencias de comportamiento por versión,
- asegurar que proyectos con blueprints de informes ejecuten pruebas desde cero,
- simplificar auditoría de dependencias requeridas.

## DTOs y mapeadores de UI viven en presentación
Se movieron los DTOs usados por interfaz (`DtoVistaClase`, `DtoVistaAtributo`) y su mapeador a `presentacion/`.
La aplicación no debe conocer estructuras de vista, porque su contrato es orquestar casos de uso, no preparar widgets.
Ubicar este mapeo en presentación reduce acoplamiento y elimina dependencias arquitectónicas inversas detectadas como P0.
Además, la UI mantiene autonomía para adaptar nombres/campos visuales sin forzar cambios en aplicación o dominio.

## Auditor de completitud: evidencia por import real y `__init__` mínimo
Se ajusta el auditor de completitud para evaluar dependencias por el módulo importado real,
en lugar de heurísticas por coincidencia textual de palabras en la línea. Con esto se evitan
falsos positivos cuando un nombre de archivo contiene términos como `infraestructura` sin
implicar una dependencia a esa capa. Además, el paquete de reglas de dependencias conserva
su API pública con imports diferidos en `__init__.py` para minimizar acoplamiento en carga.

## Compatibilidad declarativa de blueprints

**Decisión:** mover reglas de compatibilidad a metadata explícita por blueprint.

**Motivación:**
- evitar conflictos tardíos de rutas cuando ya se inició la generación;
- dar feedback temprano en UI con reglas legibles;
- reutilizar la misma validación en wizard y auditoría E2E.

**Consecuencia:**
- se agrega un registro de metadata y un caso de uso dedicado;
- la validación de compatibilidad queda desacoplada de rutas físicas.

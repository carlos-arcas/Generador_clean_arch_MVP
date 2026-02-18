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

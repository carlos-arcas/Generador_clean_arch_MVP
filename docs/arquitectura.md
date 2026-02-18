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

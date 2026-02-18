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

## Flujo
1. Presentación crea una `EspecificacionProyecto`.
2. Caso de uso `CrearPlanProyectoBase` valida y genera `PlanGeneracion`.
3. Caso de uso `EjecutarPlan` aplica el plan a través del puerto `SistemaArchivos`.
4. Infraestructura concreta (`SistemaArchivosReal`) escribe archivos de forma atómica.

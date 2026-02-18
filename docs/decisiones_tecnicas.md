# Decisiones técnicas

## Separación en CrearPlan y EjecutarPlan
Se separa la planificación de la ejecución para:
- facilitar pruebas unitarias sin IO real,
- permitir validación previa del plan,
- habilitar futuras estrategias de salida (preview, dry-run, exportación).

## Escritura atómica
Se usa escritura temporal + `replace` para reducir riesgo de corrupción en fallos intermedios. De esta manera el archivo destino se actualiza de forma íntegra.

## Uso de puertos
El puerto `SistemaArchivos` desacopla casos de uso de implementación concreta. Esto mejora testabilidad y mantiene la regla de dependencia hacia adentro.

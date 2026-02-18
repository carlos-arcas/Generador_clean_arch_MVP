# Guía de pruebas

## Suite principal
```bash
pytest --cov=. --cov-report=term-missing
```

Cobertura mínima objetivo: **85%**.

## Regresión de blueprints
Snapshots en `tests/recursos/snapshots/` verifican que las rutas de plan no cambien accidentalmente.

## Scripts
- `scripts/ejecutar_tests.bat`: cambia al root del repo, crea/activa `.venv`, instala dependencias y ejecuta:
  `pytest -q --maxfail=1 --cov=. --cov-report=term-missing --cov-fail-under=85`.
- Ejecución en Windows:

```bat
scripts\ejecutar_tests.bat
```

- Si todos los tests pasan y la cobertura alcanza el 85% mínimo, el script imprime **`TODO OK`** y termina con código `0`.
- Si hay fallo de tests, cobertura insuficiente o error en preparación del entorno, el script imprime **`FALLOS EN TESTS`** y termina con código `1`.

## Test de integración del generador
Este test valida de extremo a extremo que el caso de uso `GenerarProyectoMvp` realmente construye un proyecto funcional en disco con blueprints reales, estructura mínima obligatoria, archivos clave y `MANIFEST.json` íntegro.

También comprueba que la auditoría post-generación no reporta errores críticos, que el rollback elimina residuos cuando se simula una falla durante el plan, y que la protección ante carpeta destino no vacía lanza `ProyectoYaExisteError` sin alterar el contenido existente.

Es crítico porque blinda el flujo principal del producto: detectar regresiones en generación, trazabilidad (`MANIFEST`) y garantías de seguridad (auditoría + rollback) antes de liberar.

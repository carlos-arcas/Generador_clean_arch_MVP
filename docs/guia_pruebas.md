# Guía de pruebas

## Suite principal
```bash
pytest --cov=. --cov-report=term-missing
```

Cobertura mínima objetivo: **85%**.

## Regresión de blueprints
Snapshots en `tests/recursos/snapshots/` verifican que las rutas de plan no cambien accidentalmente.

## Scripts
- `scripts/ejecutar_tests.bat`: activa venv, instala requisitos y ejecuta pytest con coverage.

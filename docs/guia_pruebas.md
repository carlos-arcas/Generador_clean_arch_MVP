# Guía de pruebas

## Ejecución recomendada
Desde la raíz del repo ejecutar:

- `scripts\ejecutar_tests.bat`

El script realiza:
1. Creación de `.venv` si no existe.
2. Instalación de dependencias de `requirements.txt`.
3. Pruebas rápidas con `pytest -q --maxfail=1`.
4. Cobertura con `pytest --cov=. --cov-report=term-missing --cov-fail-under=85`.

Si todo sale bien devuelve `TODO OK`; de lo contrario devuelve `FALLOS EN TESTS` y un código de salida distinto de cero.

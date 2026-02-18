# Guía de pruebas

## Ejecución recomendada
Desde la raíz del repo ejecutar:

- `scripts\ejecutar_tests.bat`

El script realiza:
1. Creación de `.venv` si no existe.
2. Instalación de dependencias de `requirements.txt`.
3. Pruebas rápidas con `pytest -q --maxfail=1`.
4. Cobertura con `pytest --cov=. --cov-report=term-missing --cov-fail-under=85`.

## Nuevos bloques de pruebas
Se añadieron suites para el sistema de blueprints, manifest y auditoría:

- `tests/dominio/test_fusion_plan_generacion.py`
  - agrega/fusiona planes,
  - detecta conflictos por rutas duplicadas.
- `tests/dominio/test_manifest_proyecto.py`
  - valida invariantes de `ManifestProyecto` y `EntradaManifest`.
- `tests/aplicacion/test_crear_plan_desde_blueprints.py`
  - prueba composición de planes y fallo por conflicto.
- `tests/aplicacion/test_generar_manifest.py`
  - verifica persistencia y estructura de `manifest.json`.
- `tests/aplicacion/test_auditar_proyecto.py`
  - cubre auditoría exitosa y con faltantes.
- `tests/infraestructura/test_repositorio_blueprints_en_disco.py`
  - valida carga dinámica del blueprint base.
- `tests/infraestructura/test_calculadora_hash_real.py`
  - contrasta SHA256 real contra valor esperado.

## Objetivo de cobertura
La cobertura mínima obligatoria es **85%** y se valida en la ejecución con `pytest-cov`.


## Pruebas de presentación (v0.5.0)
Se agregan pruebas de wiring mínimas para validar integración PySide6 sin testear comportamiento visual:

- `tests/presentacion/test_wiring_basico.py`
  - instancia `VentanaPrincipal` con `QApplication` en modo `offscreen`;
  - verifica que `TrabajadorGeneracion` invoca los casos de uso esperados mediante mocks.
- `tests/presentacion/test_main.py`
  - valida que el entrypoint `python -m presentacion` construye aplicación y ventana sin levantar UI real (dobles de prueba).

Estas pruebas comprueban orquestación y contratos de integración, dejando la lógica de negocio en dominio/aplicación.

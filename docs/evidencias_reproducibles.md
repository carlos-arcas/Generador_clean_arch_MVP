# Evidencias reproducibles de validación

## Cómo validar en 2 minutos
- Windows: doble click en `scripts\validar_producto_100.bat`.
- Linux/mac: ejecutar `bash scripts/validar_producto_100.sh`.

## Qué evidencia se genera y dónde
- `docs/evidencias/auditor.txt`: salida del auditor de completitud.
- `docs/evidencias/pytest_q.txt`: salida de `pytest -q --maxfail=1`.
- `docs/evidencias/coverage.txt`: salida de cobertura con umbral mínimo 85%.

## Qué hacer si falla
- Revisar `logs/crashes.log` para el stacktrace y la causa raíz.
- Conservar y reportar el ID de incidente si la validación lo muestra.

## Evidencias de ejecución capturadas

### Auditor de completitud
```text
# Auditoría de completitud del producto

## 1) Resumen ejecutivo
- Estado general: **APROBADO**.
- Puntaje total: **60.00/60.00 (100.0%)**.
- Fallos críticos: **No**.

## 2) Tabla de puntuación por sección
| Sección | Puntaje | Estado |
|---|---:|---|
| A - Estructura y Clean Architecture | 10.00/10 | PASS |
| B - Testing y Cobertura | 10.00/10 | PASS |
| C - Scripts reproducibles Windows | 10.00/10 | PASS |
| D - Observabilidad / Logging | 10.00/10 | PASS |
| E - Documentación | 10.00/10 | PASS |
| F - UX mínima de producto | 10.00/10 | PASS |
```

### Pytest rápido
```text
........................................................................ [ 26%]
........................................................................ [ 52%]
........................................................................ [ 78%]
..........................................................               [100%]
=============================== warnings summary ===============================
tests/calidad/test_auditoria_diseno_cohesion_v4.py::test_auditoria_diseno_cohesion_v4_bloquea_regresiones_criticas
  /root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/_pytest/python.py:159: UserWarning: Auditoría v4 reporta 6 hallazgos MEDIO (no bloqueante).
    result = testfunction(**testargs)

tests/calidad/test_auditoria_v5.py::test_auditoria_diseno_cohesion_v5_bloquea_regresiones_criticas
  /root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/_pytest/python.py:159: UserWarning: Auditoría v5 reporta 1 hallazgos MEDIO (no bloqueante).
    result = testfunction(**testargs)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
274 passed, 15 skipped, 2 warnings in 2.37s
```

### Cobertura
```text
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.3.3, pluggy-1.6.0
rootdir: /workspace/Generador_clean_arch_MVP
configfile: pytest.ini
plugins: cov-5.0.0
collected 274 items / 15 skipped

tests/aplicacion/test_actualizar_manifest_patch.py .                     [  0%]
tests/aplicacion/test_agregar_atributo.py ..                             [  1%]
tests/aplicacion/test_agregar_clase.py ...                               [  2%]
tests/aplicacion/test_auditar_proyecto.py ..                             [  2%]
tests/aplicacion/test_auditar_proyecto_generado_ejecutar.py ...          [  4%]
tests/aplicacion/test_auditar_proyecto_generado_puertos.py ...           [  5%]
tests/aplicacion/test_auditor_cobertura_mock.py ..                       [  5%]
tests/aplicacion/test_auditor_estructura.py ..                           [  6%]
tests/aplicacion/test_auditor_imports.py ......                          [  8%]
tests/aplicacion/test_auditoria_generacion.py ...                        [  9%]
tests/aplicacion/test_blueprint_externo.py .                             [ 10%]
tests/aplicacion/test_casos_uso_seguridad_contratos.py .                 [ 10%]
tests/aplicacion/test_construir_especificacion_proyecto.py ....          [ 12%]
tests/aplicacion/test_construir_especificacion_validaciones.py .....     [ 13%]
tests/aplicacion/test_crear_plan_desde_blueprints.py ..                  [ 14%]
tests/aplicacion/test_crear_plan_desde_blueprints_puertos.py ...         [ 15%]
tests/aplicacion/test_crear_plan_proyecto_base.py ..                     [ 16%]
tests/aplicacion/test_credenciales_seguras.py ...                        [ 17%]
tests/aplicacion/test_editar_atributo.py ..                              [ 18%]
tests/aplicacion/test_ejecutar_plan.py ...                               [ 19%]
tests/aplicacion/test_eliminar_atributo.py ..                            [ 20%]
tests/aplicacion/test_eliminar_clase.py ..                               [ 20%]
tests/aplicacion/test_errores_contratos.py ..                            [ 21%]
tests/aplicacion/test_generacion_segura.py ...                           [ 22%]
tests/aplicacion/test_generar_manifest.py .                              [ 22%]
tests/aplicacion/test_generar_proyecto_mvp.py .                          [ 23%]
tests/aplicacion/test_generar_proyecto_mvp_pipeline.py ......            [ 25%]
tests/aplicacion/test_generar_proyecto_mvp_puertos.py ...                [ 26%]
tests/aplicacion/test_gestion_clases_contratos.py ..                     [ 27%]
tests/aplicacion/test_guardar_cargar_preset.py .                         [ 27%]
tests/aplicacion/test_intercambiabilidad_persistencia.py ..              [ 28%]
tests/aplicacion/test_motor_validacion.py ........                       [ 31%]
tests/aplicacion/test_pasos_generacion_contratos.py ....                 [ 32%]
tests/aplicacion/test_patch_clase_existente_error.py .                   [ 33%]
tests/aplicacion/test_patch_nueva_clase.py .                             [ 33%]
tests/aplicacion/test_presets.py .....                                   [ 35%]
tests/aplicacion/test_puertos_contratos.py ..                            [ 36%]
tests/aplicacion/test_reglas_dependencias.py .....                       [ 37%]
tests/aplicacion/test_reglas_dependencias_contratos.py ..                [ 38%]
tests/aplicacion/test_renombrar_clase.py ..                              [ 39%]
tests/aplicacion/test_taxonomia_errores.py ....                          [ 40%]
tests/aplicacion/test_validacion_contratos.py .                          [ 41%]
tests/aplicacion/test_validador_imports.py .......                       [ 43%]
tests/arquitectura/test_composition_root.py ...                          [ 44%]
tests/arquitectura/test_dependencias_capas.py .                          [ 45%]
tests/blueprints/test_contenido_blueprints.py ....                       [ 46%]
tests/blueprints/test_crud_json_blueprint.py ..                          [ 47%]
tests/blueprints/test_crud_sqlite_blueprint.py ...                       [ 48%]
tests/blueprints/test_export_csv_blueprint.py ..                         [ 49%]
tests/blueprints/test_export_excel_blueprint.py ..                       [ 50%]
tests/blueprints/test_export_pdf_blueprint.py ...                        [ 51%]
tests/blueprints/test_repositorio_json_contenido.py ...                  [ 52%]
tests/calidad/test_auditor_completitud_producto.py ....                  [ 53%]
tests/calidad/test_auditoria_diseno_cohesion.py .                        [ 54%]
tests/calidad/test_auditoria_diseno_cohesion_v3.py .                     [ 54%]
tests/calidad/test_auditoria_diseno_cohesion_v4.py .                     [ 54%]
tests/calidad/test_auditoria_v5.py .                                     [ 55%]
tests/calidad/test_cohesion_errores.py ..                                [ 55%]
tests/calidad/test_no_acceso_privados_ajenos.py .                        [ 56%]
tests/dominio/test_especificacion_atributo.py ....                       [ 57%]
tests/dominio/test_especificacion_clase.py .....                         [ 59%]
tests/dominio/test_especificacion_proyecto.py ....                       [ 60%]
tests/dominio/test_fusion_plan_generacion.py ..                          [ 61%]
tests/dominio/test_manifest_proyecto.py ....                             [ 63%]
tests/dominio/test_plan_generacion.py ...                                [ 64%]
tests/dominio/test_plan_generacion_contratos.py ..                       [ 64%]
tests/dominio/test_reglas_duplicados.py ...                              [ 66%]
tests/herramientas/test_capturar_evidencias.py ...                       [ 67%]
tests/infraestructura/test_almacen_presets_disco.py .                    [ 67%]
tests/infraestructura/test_bootstrap.py ..                               [ 68%]
tests/infraestructura/test_bootstrap_cli.py ...                          [ 69%]
tests/infraestructura/test_bootstrap_gui.py ...                          [ 70%]
tests/infraestructura/test_calculadora_hash_real.py .                    [ 70%]
tests/infraestructura/test_descubridor_plugins.py ...                    [ 71%]
tests/infraestructura/test_ejecutor_procesos_subprocess.py .             [ 72%]
tests/infraestructura/test_filtro_logs.py .                              [ 72%]
tests/infraestructura/test_logging_config.py ..                          [ 73%]
tests/infraestructura/test_manejo_errores_credenciales.py ..             [ 74%]
tests/infraestructura/test_repositorio_blueprints_en_disco.py ..         [ 74%]
tests/integracion/test_auditoria_completa.py .                           [ 75%]
tests/integracion/test_concurrencia_basica.py .                          [ 75%]
tests/integracion/test_fallos_hostiles.py ...                            [ 76%]
tests/integracion/test_generacion_completa.py .                          [ 77%]
tests/integracion/test_generacion_mvp_completa.py ...                    [ 78%]
tests/integracion/test_runtime_v6_integracion.py .......                 [ 80%]
tests/integracion/test_wizard_orquestador.py .                           [ 81%]
tests/presentacion/test_acciones_soporte.py ...                          [ 82%]
tests/presentacion/test_cli_argumentos.py ...                            [ 83%]
tests/presentacion/test_cli_comando_generar.py ......                    [ 85%]
tests/presentacion/test_id_incidente.py .                                [ 85%]
tests/presentacion/test_manejo_errores_wizard.py ...                     [ 86%]
tests/presentacion/test_mapeador_dominio_a_vista.py ....                 [ 88%]
tests/presentacion/test_mapeo_mensajes_error.py ...                      [ 89%]
tests/presentacion/test_modelos_qt.py ..                                 [ 90%]
tests/presentacion/test_modelos_qt_sin_dominio.py ...                    [ 91%]
tests/presentacion/test_orquestador_finalizacion_refactor.py .......     [ 93%]
tests/presentacion/test_orquestador_finalizacion_wizard.py ...           [ 94%]
tests/presentacion/test_presets_sin_acceso_privado.py ...                [ 95%]
tests/presentacion/test_trabajador_generacion_errores.py ...             [ 97%]
tests/regresion/test_snapshot_rutas_plan.py ..                           [ 97%]
tests/scripts/test_scripts_existentes.py ..                              [ 98%]
tests/snapshots/test_blueprints_golden.py ..                             [ 99%]
tests/snapshots/test_blueprints_snapshot.py ..                           [100%]

=============================== warnings summary ===============================
tests/calidad/test_auditoria_diseno_cohesion_v4.py::test_auditoria_diseno_cohesion_v4_bloquea_regresiones_criticas
  /root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/_pytest/python.py:159: UserWarning: Auditoría v4 reporta 6 hallazgos MEDIO (no bloqueante).
    result = testfunction(**testargs)

tests/calidad/test_auditoria_v5.py::test_auditoria_diseno_cohesion_v5_bloquea_regresiones_criticas
  /root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/_pytest/python.py:159: UserWarning: Auditoría v5 reporta 1 hallazgos MEDIO (no bloqueante).
    result = testfunction(**testargs)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html

---------- coverage: platform linux, python 3.12.12-final-0 ----------
Name                                                                                                Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------------------------------------------------------------
aplicacion/__init__.py                                                                                  0      0   100%
aplicacion/casos_uso/__init__.py                                                                        0      0   100%
aplicacion/casos_uso/actualizar_manifest_patch.py                                                      27      0   100%
aplicacion/casos_uso/auditar_proyecto_generado.py                                                     183     10    95%   55-59, 100, 110, 132, 135, 200
aplicacion/casos_uso/auditoria/__init__.py                                                              2      0   100%
aplicacion/casos_uso/auditoria/auditar_proyecto_generado.py                                            80     17    79%   74, 82, 93, 108, 115, 119-120, 123, 135-153
aplicacion/casos_uso/auditoria/reglas_dependencias/__init__.py                                         10      1    90%   32
aplicacion/casos_uso/auditoria/reglas_dependencias/regla_aplicacion_no_depende_infraestructura.py      28      2    93%   34-35
aplicacion/casos_uso/auditoria/reglas_dependencias/regla_base.py                                        6      0   100%
aplicacion/casos_uso/auditoria/reglas_dependencias/regla_dominio_no_depende_de_otras_capas.py          28      2    93%   34-35
aplicacion/casos_uso/auditoria/reglas_dependencias/regla_no_imports_circulares.py                       7      0   100%
aplicacion/casos_uso/auditoria/reglas_dependencias/regla_presentacion_no_depende_dominio.py            28      2    93%   34-35
aplicacion/casos_uso/auditoria/validadores/__init__.py                                                  3      0   100%
aplicacion/casos_uso/auditoria/validadores/validador_base.py                                           14      0   100%
aplicacion/casos_uso/auditoria/validadores/validador_imports.py                                        80      1    99%   71
aplicacion/casos_uso/construir_especificacion_proyecto.py                                              65      3    95%   27, 104-105
aplicacion/casos_uso/consultar_catalogo_blueprints.py                                                  12      0   100%
aplicacion/casos_uso/crear_plan_desde_blueprints.py                                                    49      4    92%   20, 54, 58-59
aplicacion/casos_uso/crear_plan_patch_desde_blueprints.py                                              44      6    86%   33, 46, 64-65, 67, 69
aplicacion/casos_uso/crear_plan_proyecto_base.py                                                       14      0   100%
aplicacion/casos_uso/ejecutar_plan.py                                                                  24      0   100%
aplicacion/casos_uso/generacion/__init__.py                                                             2      0   100%
aplicacion/casos_uso/generacion/generar_proyecto_mvp.py                                                62      0   100%
aplicacion/casos_uso/generacion/pasos/__init__.py                                                       0      0   100%
aplicacion/casos_uso/generacion/pasos/ejecutar_auditoria.py                                            11      0   100%
aplicacion/casos_uso/generacion/pasos/ejecutar_plan.py                                                 21      0   100%
aplicacion/casos_uso/generacion/pasos/errores_pipeline.py                                               3      0   100%
aplicacion/casos_uso/generacion/pasos/normalizar_entrada.py                                            27      2    93%   55-56
aplicacion/casos_uso/generacion/pasos/preparar_estructura.py                                           19      0   100%
aplicacion/casos_uso/generacion/pasos/publicar_manifest.py                                             14      1    93%   24
aplicacion/casos_uso/generacion/pasos/rollback_generacion.py                                            9      1    89%   14
aplicacion/casos_uso/generacion/pasos/validar_entrada.py                                               24      3    88%   24, 28, 30
aplicacion/casos_uso/generar_manifest.py                                                               28      0   100%
aplicacion/casos_uso/gestion_clases/__init__.py                                                         5      0   100%
aplicacion/casos_uso/gestion_clases/agregar_clase.py                                                   30      0   100%
aplicacion/casos_uso/gestion_clases/base.py                                                             5      0   100%
aplicacion/casos_uso/gestion_clases/eliminar_clase.py                                                  28      0   100%
aplicacion/casos_uso/gestion_clases/modificar_clase.py                                                 30      0   100%
aplicacion/casos_uso/gestion_clases/validaciones_clase.py                                              21      3    86%   26-28
aplicacion/casos_uso/presets/__init__.py                                                               12      5    58%   11, 18-21
aplicacion/casos_uso/presets/cargar_preset_proyecto.py                                                 13      0   100%
aplicacion/casos_uso/presets/guardar_preset_proyecto.py                                                19      4    79%   22-23, 35-41
aplicacion/casos_uso/seguridad/__init__.py                                                              5      0   100%
aplicacion/casos_uso/seguridad/eliminar_credencial.py                                                   7      0   100%
aplicacion/casos_uso/seguridad/guardar_credencial.py                                                   10      1    90%   20
aplicacion/casos_uso/seguridad/obtener_credencial.py                                                    8      0   100%
aplicacion/casos_uso/seguridad/repositorio_credenciales.py                                              4      0   100%
aplicacion/dtos/__init__.py                                                                             0      0   100%
aplicacion/dtos/proyecto/__init__.py                                                                    4      0   100%
aplicacion/dtos/proyecto/dto_atributo.py                                                                7      0   100%
aplicacion/dtos/proyecto/dto_clase.py                                                                   7      0   100%
aplicacion/dtos/proyecto/dto_proyecto_entrada.py                                                       10      0   100%
aplicacion/errores/__init__.py                                                                          5      0   100%
aplicacion/errores/errores_auditoria.py                                                                 3      0   100%
aplicacion/errores/errores_generacion.py                                                                6      0   100%
aplicacion/errores/errores_pipeline.py                                                                  8      0   100%
aplicacion/errores/errores_validacion.py                                                                4      0   100%
aplicacion/puertos/__init__.py                                                                          0      0   100%
aplicacion/puertos/almacen_presets.py                                                                  10      0   100%
aplicacion/puertos/blueprint.py                                                                        18      0   100%
aplicacion/puertos/calculadora_hash.py                                                                  5      0   100%
aplicacion/puertos/calculadora_hash_puerto.py                                                           5      0   100%
aplicacion/puertos/descubridor_plugins_puerto.py                                                        7      0   100%
aplicacion/puertos/ejecutor_procesos.py                                                                11      0   100%
aplicacion/puertos/generador_manifest_puerto.py                                                         5      0   100%
aplicacion/puertos/manifest.py                                                                          9      0   100%
aplicacion/puertos/repositorio_especificacion_proyecto.py                                               8      0   100%
aplicacion/puertos/sistema_archivos.py                                                                  7      0   100%
aplicacion/validacion/__init__.py                                                                       4      0   100%
aplicacion/validacion/motor_validacion.py                                                              13      0   100%
aplicacion/validacion/regla_validacion.py                                                               5      1    80%   12
aplicacion/validacion/resultado_validacion.py                                                           7      0   100%
blueprints/__init__.py                                                                                  0      0   100%
blueprints/base_clean_arch_v1/__init__.py                                                               2      0   100%
blueprints/base_clean_arch_v1/blueprint.py                                                             14      0   100%
blueprints/crud_json_v1/__init__.py                                                                     2      0   100%
blueprints/crud_json_v1/blueprint.py                                                                  158     14    91%   107, 114-116, 119, 136, 205, 523, 526, 543-547
blueprints/crud_sqlite_v1/__init__.py                                                                   2      0   100%
blueprints/crud_sqlite_v1/blueprint.py                                                                 69      0   100%
blueprints/export_csv_v1/__init__.py                                                                    0      0   100%
blueprints/export_csv_v1/blueprint.py                                                                  57      6    89%   79, 86-88, 91-100
blueprints/export_excel_v1/__init__.py                                                                  0      0   100%
blueprints/export_excel_v1/blueprint.py                                                                54      4    93%   77, 84-86
blueprints/export_pdf_v1/__init__.py                                                                    0      0   100%
blueprints/export_pdf_v1/blueprint.py                                                                  55      4    93%   77, 84-86
bootstrap/__init__.py                                                                                   2      2     0%   3-5
bootstrap/composition_root.py                                                                           5      5     0%   3-22
dominio/__init__.py                                                                                     0      0   100%
dominio/errores.py                                                                                      4      0   100%
dominio/especificacion.py                                                                             103      7    93%   30, 49, 51, 53, 62, 105, 137
dominio/excepciones/__init__.py                                                                         2      0   100%
dominio/excepciones/proyecto_ya_existe_error.py                                                         3      0   100%
dominio/manifest.py                                                                                    38      2    95%   20, 53
dominio/modelos.py                                                                                      4      0   100%
dominio/plan_generacion.py                                                                             25      0   100%
dominio/preset/__init__.py                                                                              2      0   100%
dominio/preset/preset_proyecto.py                                                                      15      2    87%   23, 26
dominio/seguridad/__init__.py                                                                           2      0   100%
dominio/seguridad/credencial.py                                                                        20      2    90%   25, 43
herramientas/__init__.py                                                                                0      0   100%
herramientas/auditar_completitud_producto.py                                                          509     87    83%   77-80, 101, 113, 122-123, 138, 141, 168, 170, 172-175, 194, 217-218, 226, 232-233, 249-250, 263-264, 282-283, 306-307, 313-314, 329-330, 332-333, 344-345, 351, 354, 358-359, 387-388, 407-408, 423-424, 446-447, 449-450, 452-453, 464-465, 511-512, 525-526, 530-532, 538-539, 556-558, 569, 573-574, 591-592, 604-605, 670, 688-689, 733-736, 743, 758-760, 764
herramientas/auditar_diseno_cohesion.py                                                               146     17    88%   49-50, 82, 108, 129, 152-154, 187, 239, 251-252, 260, 291-294
herramientas/auditar_diseno_cohesion_v3.py                                                            179     34    81%   52-53, 73-74, 107, 111, 121, 134, 151, 157, 161-162, 180-181, 193, 214, 216, 220-222, 256-269, 273-283, 287
herramientas/auditar_diseno_cohesion_v4.py                                                            216     42    81%   45-46, 72-74, 80, 91, 97, 126, 128, 138, 150, 157, 159, 162, 179, 190, 192, 196, 217, 219, 223, 240-242, 255-257, 288-292, 296-306, 310
herramientas/auditar_diseno_cohesion_v5.py                                                            275     56    80%   54-55, 73-75, 81, 92, 98, 127, 129, 131, 141, 154, 161, 163, 166, 168, 183, 194, 196, 200, 221, 223, 227, 245-247, 249, 258-261, 274-277, 282, 300, 321, 337-339, 373-377, 381-391, 395
herramientas/capturar_evidencias.py                                                                    82     20    76%   21-25, 52-64, 138-141, 151-153, 157-158, 162
infraestructura/__init__.py                                                                             0      0   100%
infraestructura/almacen_presets_disco.py                                                                2      0   100%
infraestructura/bootstrap/__init__.py                                                                  22      0   100%
infraestructura/bootstrap/bootstrap_base.py                                                            47      0   100%
infraestructura/bootstrap/bootstrap_cli.py                                                             28      0   100%
infraestructura/bootstrap/bootstrap_gui.py                                                             19      0   100%
infraestructura/calculadora_hash_real.py                                                               10      0   100%
infraestructura/ejecutor_procesos_subprocess.py                                                         7      0   100%
infraestructura/errores.py                                                                              4      0   100%
infraestructura/logging_config.py                                                                      44      4    91%   73-76
infraestructura/manifest/__init__.py                                                                    2      0   100%
infraestructura/manifest/generador_manifest.py                                                         16      1    94%   43
infraestructura/manifest_en_disco.py                                                                   29      2    93%   20, 59
infraestructura/plugins/__init__.py                                                                     0      0   100%
infraestructura/plugins/descubridor_plugins.py                                                         87     15    83%   41, 44, 53, 66, 82, 86, 97, 107-109, 114-115, 127-129
infraestructura/presets/__init__.py                                                                     2      0   100%
infraestructura/presets/repositorio_presets_json.py                                                    51      3    94%   42, 48, 58
infraestructura/repositorio_blueprints_en_disco.py                                                     34      4    88%   21, 27, 31, 51
infraestructura/repositorio_especificacion_proyecto_en_memoria.py                                      10      0   100%
infraestructura/seguridad/__init__.py                                                                   4      0   100%
infraestructura/seguridad/fabrica_repositorio_credenciales.py                                          21      0   100%
infraestructura/seguridad/repositorio_credenciales_memoria.py                                          11      1    91%   21
infraestructura/seguridad/repositorio_credenciales_windows.py                                          67     56    16%   12-31, 38-56, 59-76, 79-94, 97-102
infraestructura/sistema_archivos_real.py                                                               18      1    94%   28
---------------------------------------------------------------------------------------------------------------------------------
TOTAL                                                                                                3869    460    88%

Required test coverage of 85% reached. Total coverage: 88.11%
================= 274 passed, 15 skipped, 2 warnings in 5.18s ==================

[stderr]
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/__init__.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/__init__.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/feature.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/feature.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/__init__.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/__init__.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/errorhandler.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/errorhandler.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/importhandler.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/importhandler.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/layout.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/layout.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/lib/__init__.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/lib/__init__.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/lib/enum_sig.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/lib/enum_sig.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/lib/pyi_generator.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/lib/pyi_generator.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/lib/tool.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/lib/tool.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/loader.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/loader.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/mapping.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/mapping.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/parser.py': No source for code: '/workspace/Generador_clean_arch_MVP/shibokensupport/signature/parser.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
/root/.pyenv/versions/3.12.12/lib/python3.12/site-packages/coverage/report_core.py:113: CoverageWarning: Couldn't parse '/workspace/Generador_clean_arch_MVP/signature_bootstrap.py': No source for code: '/workspace/Generador_clean_arch_MVP/signature_bootstrap.py'. (couldnt-parse); see https://coverage.readthedocs.io/en/7.13.4/messages.html#warning-couldnt-parse
  coverage._warn(msg, slug="couldnt-parse")
```

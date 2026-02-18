# Generador Base Proyectos (v1.6.0)

Herramienta para generar proyectos base con Clean Architecture a partir de blueprints combinables.

## Modos disponibles
- **UI (PySide6)**: wizard con generación real en background.
- **CLI**: alternativa no visual que reutiliza los mismos casos de uso del core.

## Blueprints soportados
- `base_clean_arch`
- `crud_json`
- `crud_sqlite`
- `export_csv`
- `export_excel`
- `export_pdf`

## Cómo generar un proyecto desde UI
1. Ejecuta `python -m presentacion` y completa nombre/ruta/clases en el wizard.
2. En el resumen, pulsa **Finalizar** para lanzar la generación MVP (`base_clean_arch_v1 + crud_json_v1`) en segundo plano.
3. Espera el mensaje final: **Proyecto generado correctamente** o **Falló la generación (ver logs)**.

## Presets
Los presets se guardan en `configuracion/presets/*.json` e incluyen:
- especificación del proyecto (opcionalmente sin ruta destino),
- clases y atributos,
- blueprints,
- opciones (incluido patch cuando aplique).

## Auditoría
El auditor valida estructura, imports, logging, cobertura y consistencia de `manifest.json` + hashes.
Siempre genera `docs/informe_auditoria.md` con estado **APROBADO** o **RECHAZADO**.

## Experiencia de generación
- **Progreso por etapas**: el wizard informa cada fase real (validación, plan, ejecución, manifest, auditoría y finalización) con barra en modo ocupado sin bloquear la UI.
- **Cancelación segura**: durante la ejecución aparece el botón **Cancelar generación**; la cancelación es cooperativa y ejecuta rollback de carpeta parcial si aplica.
- **Auditoría automática**: al final se muestran errores y warnings detectados por la auditoría post-generación.
- **Logs y crashes**: ante fallos revisa `logs/` y, para excepciones no controladas, el detalle técnico queda en `logs/crashes.log`.

## Ejecución rápida
### UI
```bash
python -m presentacion
```

### CLI
```bash
python -m presentacion.cli generar --preset configuracion/presets/mi_preset.json --destino salida/proyecto
python -m presentacion.cli validar-preset --preset configuracion/presets/mi_preset.json
python -m presentacion.cli auditar --proyecto salida/proyecto
```

### Tests
```bash
pytest --cov=. --cov-report=term-missing
```

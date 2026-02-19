from __future__ import annotations

import json
from pathlib import Path

from infraestructura.bootstrap.bootstrap_cli import construir_contenedor_cli


def _preset_conflictivo(tmp_path: Path) -> Path:
    ruta = tmp_path / "preset_conflictivo.json"
    ruta.write_text(
        json.dumps(
            {
                "especificacion": {
                    "nombre_proyecto": "demo_conflictos",
                    "descripcion": "",
                    "version": "1.0.0",
                    "clases": [{"nombre": "Persona", "atributos": []}],
                },
                "blueprints": ["crud_json", "crud_sqlite"],
            }
        ),
        encoding="utf-8",
    )
    return ruta


def test_auditor_finalizacion_conflictos_rutas_seleccionar_todos(tmp_path: Path) -> None:
    contenedor = construir_contenedor_cli()
    salida = contenedor.auditar_finalizacion_proyecto.ejecutar(
        ruta_preset=str(_preset_conflictivo(tmp_path)),
        ruta_sandbox=str(tmp_path / "sandbox"),
        ruta_evidencias=str(tmp_path / "evidencias"),
        ejecutar_smoke_test=False,
        ejecutar_auditoria_arquitectura=False,
    )

    assert salida.estado_global == "FAIL"
    assert salida.tipo_fallo_dominante == "CONFLICTO"
    assert salida.codigo_fallo == "CON-001"
    assert salida.conflictos_rutas.total > 0
    top = "\n".join(salida.conflictos_rutas.ejemplos_top)
    assert "crud_json" in top and "crud_sqlite" in top
    etapa_generacion = next(etapa for etapa in salida.etapas if etapa.nombre == "Generación sandbox")
    assert etapa_generacion.estado == "SKIP"

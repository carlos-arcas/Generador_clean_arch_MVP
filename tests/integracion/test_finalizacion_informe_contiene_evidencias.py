from __future__ import annotations

from aplicacion.dtos.auditoria import ConflictosFinalizacion, DtoAuditoriaFinalizacionSalida, ResultadoEtapa
from aplicacion.servicios.generador_informe_finalizacion_md import generar_markdown


def test_finalizacion_informe_contiene_evidencias() -> None:
    salida = DtoAuditoriaFinalizacionSalida(
        id_ejecucion="AUD-20260101-000000-ABCD",
        ruta_sandbox="/tmp/sandbox",
        etapas=[
            ResultadoEtapa("Preparación", "PASS", 10, "OK"),
            ResultadoEtapa("Preflight conflictos de rutas", "FAIL", 5, "Duplicadas", tipo_fallo="CONFLICTO", codigo="CON-001", mensaje_usuario="duplicadas"),
        ],
        conflictos=ConflictosFinalizacion(
            total_rutas_duplicadas=1,
            rutas_duplicadas=["app/persona.py"],
            rutas_por_blueprint={"app/persona.py": ["crud_a", "crud_b"]},
        ),
        evidencias={
            "meta_fecha_iso": "2026-01-01T00:00:00",
            "ruta_evidencias": "docs/evidencias_finalizacion/AUD-20260101-000000-ABCD",
            "meta_ruta_preset": "preset.json",
            "meta_comando": "python -m presentacion.cli auditar-finalizacion --preset preset.json --sandbox /tmp/sandbox",
            "preparacion": "ok",
            "carga_preset": "ok",
            "preflight_validacion_entrada": "ok",
            "preflight_conflictos_rutas": "duplicadas",
            "generacion_sandbox": "skip",
            "auditoria_arquitectura": "skip",
            "smoke_test": "skip",
        },
    )

    markdown = generar_markdown(salida)

    assert "ID ejecución" in markdown
    assert "| Preflight conflictos de rutas | FAIL |" in markdown
    assert "Preflight Conflictos Rutas" in markdown
    assert "app/persona.py -> [crud_a, crud_b]" in markdown

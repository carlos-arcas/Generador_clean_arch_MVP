from __future__ import annotations

from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionSalida, ResultadoEtapa
from aplicacion.servicios.generador_informe_finalizacion_md import generar_markdown


def test_informe_incluye_estado_global_y_duraciones_no_cero() -> None:
    salida = DtoAuditoriaFinalizacionSalida(
        id_ejecucion="AUD-20260101-000000-ABCD",
        ruta_sandbox="/tmp/sandbox",
        etapas=[
            ResultadoEtapa("Preparación", "PASS", 1, "Contexto listo"),
            ResultadoEtapa("Carga preset", "PASS", 2, "Blueprints: 3"),
            ResultadoEtapa("Preflight validación entrada", "PASS", 3, "Validación de entrada OK"),
            ResultadoEtapa(
                "Preflight conflictos de rutas",
                "FAIL",
                4,
                "Rutas duplicadas detectadas",
                tipo_fallo="CONFLICTO",
                codigo="CON-001",
                mensaje_usuario="Se detectaron rutas duplicadas entre blueprints.",
            ),
        ],
        conflictos=None,
        evidencias={
            "meta_fecha_iso": "2026-01-01T00:00:00",
            "ruta_evidencias": "docs/evidencias_finalizacion/AUD-20260101-000000-ABCD",
            "meta_ruta_preset": "preset.json",
            "meta_comando": "python -m presentacion.cli auditar-finalizacion --preset preset.json --sandbox /tmp/sandbox",
        },
    )

    markdown = generar_markdown(salida)

    assert "## Estado global" in markdown
    assert "Duración ms" in markdown
    assert "| Preparación | PASS | 1 |" in markdown
    assert "| Preflight conflictos de rutas | FAIL | 4 |" in markdown

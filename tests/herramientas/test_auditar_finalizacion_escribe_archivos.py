from __future__ import annotations

from pathlib import Path

from aplicacion.dtos.auditoria import DtoAuditoriaFinalizacionSalida, ResultadoEtapa
from herramientas.auditar_finalizacion_e2e import ejecutar_auditoria_finalizacion


def test_auditar_finalizacion_escribe_archivos(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    salida_falsa = DtoAuditoriaFinalizacionSalida(
        id_ejecucion="AUD-20260101-010101-AAAA",
        ruta_sandbox=str(tmp_path / "sandbox"),
        etapas=[ResultadoEtapa("Preparación", "PASS", 1, "ok")],
        conflictos=None,
        evidencias={
            "meta_fecha_iso": "2026-01-01T01:01:01",
            "ruta_evidencias": "docs/evidencias_finalizacion/AUD-20260101-010101-AAAA",
            "meta_ruta_preset": "preset.json",
            "meta_comando": "cmd",
            "preparacion": "ok",
            "carga_preset": "ok",
            "preflight_conflictos": "ok",
            "generacion_sandbox": "ok",
            "auditoria_arquitectura": "ok",
            "smoke_test": "ok",
        },
    )

    ejecutar_auditoria_finalizacion(
        preset="preset.json",
        sandbox=str(tmp_path / "sandbox"),
        ejecutor=lambda _: salida_falsa,
    )

    assert (tmp_path / "docs" / "auditoria_finalizacion_e2e.md").exists()
    ruta_evidencias = tmp_path / "docs" / "evidencias_finalizacion" / salida_falsa.id_ejecucion
    assert (ruta_evidencias / "preflight_conflictos.txt").exists()
    assert (ruta_evidencias / "compileall.txt").exists()
    assert (ruta_evidencias / "pytest_generado.txt").exists()
    assert (ruta_evidencias / "auditoria_arquitectura.txt").exists()

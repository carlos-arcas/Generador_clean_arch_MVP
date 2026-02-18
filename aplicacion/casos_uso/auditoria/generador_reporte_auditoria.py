"""Generación de reporte final de auditoría CLI."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


class GeneradorReporteAuditoria:
    """Construye informe markdown de auditoría en docs/."""

    def escribir(
        self,
        *,
        base: Path,
        blueprints: list[str],
        errores: list[str],
        cobertura: float | None,
        codigo_salida_pytest: int,
        stdout_pytest: str,
        conclusion: str,
    ) -> None:
        ruta_docs = base / "docs"
        ruta_docs.mkdir(parents=True, exist_ok=True)
        ruta_informe = ruta_docs / "informe_auditoria.md"

        estructura_ok = "OK" if not any("recurso obligatorio" in e for e in errores) else "ERROR"
        arquitectura_ok = "OK" if not any("Import" in e or "circular" in e for e in errores) else "ERROR"
        logging_ok = "OK" if not any("logging" in e or "logs/" in e for e in errores) else "ERROR"
        manifest_ok = "OK" if not any("manifest" in e or "Hash" in e for e in errores) else "ERROR"

        contenido = (
            "# Informe de Auditoría\n\n"
            "## Fecha\n"
            f"{datetime.now().isoformat(timespec='seconds')}\n\n"
            "## Blueprints usados\n"
            f"{', '.join(blueprints) if blueprints else 'No informado'}\n\n"
            "## Validación de estructura\n"
            f"Resultado: {estructura_ok}\n\n"
            "## Validación de arquitectura (imports)\n"
            f"Resultado: {arquitectura_ok}\n\n"
            "## Validación logging\n"
            f"Resultado: {logging_ok}\n\n"
            "## Consistencia manifest/hash\n"
            f"Resultado: {manifest_ok}\n\n"
            "## Resultado pytest\n"
            f"Código de salida: {codigo_salida_pytest}\n\n"
            "```\n"
            f"{stdout_pytest.strip()}\n"
            "```\n\n"
            "## Cobertura total\n"
            f"{f'{cobertura:.2f}%' if cobertura is not None else 'No disponible'}\n\n"
            "## Conclusión final (APROBADO / RECHAZADO)\n"
            f"{conclusion}\n\n"
        )
        if errores:
            contenido += "### Errores detectados\n\n"
            for error in errores:
                contenido += f"- {error}\n"
        ruta_informe.write_text(contenido, encoding="utf-8")

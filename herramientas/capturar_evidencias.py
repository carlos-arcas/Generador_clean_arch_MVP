from __future__ import annotations

import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

Comando = Sequence[str]
EjecutorSubproceso = Callable[[Comando, Path], "ResultadoEjecucion"]


@dataclass(frozen=True)
class ResultadoEjecucion:
    codigo_retorno: int
    salida: str


def _resolver_raiz_repo() -> Path:
    actual = Path.cwd().resolve()
    for candidato in [actual, *actual.parents]:
        if (candidato / ".git").exists():
            return candidato
    return actual


def _configurar_logger(ruta_repo: Path) -> logging.Logger:
    logger = logging.getLogger("capturar_evidencias")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    carpeta_logs = ruta_repo / "logs"
    carpeta_logs.mkdir(parents=True, exist_ok=True)
    formato = logging.Formatter("%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s")

    handler_info = logging.FileHandler(carpeta_logs / "seguimiento.log", encoding="utf-8")
    handler_info.setLevel(logging.INFO)
    handler_info.setFormatter(formato)

    handler_error = logging.FileHandler(carpeta_logs / "crashes.log", encoding="utf-8")
    handler_error.setLevel(logging.ERROR)
    handler_error.setFormatter(formato)

    logger.addHandler(handler_info)
    logger.addHandler(handler_error)
    return logger


def _ejecutor_real(comando: Comando, ruta_repo: Path) -> ResultadoEjecucion:
    resultado = subprocess.run(
        list(comando),
        cwd=ruta_repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    salida_unificada = (resultado.stdout or "")
    if resultado.stderr:
        salida_unificada = f"{salida_unificada}\n[stderr]\n{resultado.stderr}".strip()
    return ResultadoEjecucion(codigo_retorno=resultado.returncode, salida=salida_unificada.strip() + "\n")


def _escribir_evidencia(ruta: Path, contenido: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf-8")


def _renderizar_documento(ruta_repo: Path) -> str:
    base = ruta_repo / "docs" / "evidencias"
    auditor = (base / "auditor.txt").read_text(encoding="utf-8") if (base / "auditor.txt").exists() else ""
    pytest_q = (base / "pytest_q.txt").read_text(encoding="utf-8") if (base / "pytest_q.txt").exists() else ""
    coverage = (base / "coverage.txt").read_text(encoding="utf-8") if (base / "coverage.txt").exists() else ""

    secciones = [
        "# Evidencias reproducibles de validación",
        "",
        "## Cómo validar en 2 minutos",
        "- Windows: doble click en `scripts\\validar_producto_100.bat`.",
        "- Linux/mac: ejecutar `bash scripts/validar_producto_100.sh`.",
        "",
        "## Qué evidencia se genera y dónde",
        "- `docs/evidencias/auditor.txt`: salida del auditor de completitud.",
        "- `docs/evidencias/pytest_q.txt`: salida de `pytest -q --maxfail=1`.",
        "- `docs/evidencias/coverage.txt`: salida de cobertura con umbral mínimo 85%.",
        "",
        "## Qué hacer si falla",
        "- Revisar `logs/crashes.log` para el stacktrace y la causa raíz.",
        "- Conservar y reportar el ID de incidente si la validación lo muestra.",
        "",
        "## Evidencias de ejecución capturadas",
        "",
        "### Auditor de completitud",
        "```text",
        auditor.rstrip(),
        "```",
        "",
        "### Pytest rápido",
        "```text",
        pytest_q.rstrip(),
        "```",
        "",
        "### Cobertura",
        "```text",
        coverage.rstrip(),
        "```",
        "",
    ]
    return "\n".join(secciones)


def capturar_evidencias_reproducibles(
    ruta_repo: Path,
    ejecutor: EjecutorSubproceso | None = None,
) -> int:
    logger = _configurar_logger(ruta_repo)
    ejecutor_efectivo = ejecutor or _ejecutor_real

    comandos = [
        ("auditor", [sys.executable, "-m", "herramientas.auditar_completitud_producto"], ruta_repo / "docs" / "evidencias" / "auditor.txt"),
        ("pytest_q", [sys.executable, "-m", "pytest", "-q", "--maxfail=1"], ruta_repo / "docs" / "evidencias" / "pytest_q.txt"),
        (
            "coverage",
            [sys.executable, "-m", "pytest", "--cov=.", "--cov-report=term-missing", "--cov-fail-under=85"],
            ruta_repo / "docs" / "evidencias" / "coverage.txt",
        ),
    ]

    try:
        for nombre, comando, ruta_salida in comandos:
            logger.info("Ejecutando comando de evidencia %s: %s", nombre, " ".join(comando))
            resultado = ejecutor_efectivo(comando, ruta_repo)
            salida = resultado.salida
            if nombre == "auditor" and not salida.strip():
                ruta_informe = ruta_repo / "docs" / "auditoria_completitud_producto.md"
                if ruta_informe.exists():
                    lineas = ruta_informe.read_text(encoding="utf-8").splitlines()
                    salida = "\n".join(lineas[:16]).strip() + "\n"
            _escribir_evidencia(ruta_salida, salida)
            if resultado.codigo_retorno != 0:
                logger.error("Comando %s falló con código %s", nombre, resultado.codigo_retorno)
                return 1

        contenido_doc = _renderizar_documento(ruta_repo)
        _escribir_evidencia(ruta_repo / "docs" / "evidencias_reproducibles.md", contenido_doc)
        logger.info("Documento docs/evidencias_reproducibles.md actualizado")
        return 0
    except Exception:
        logger.exception("Fallo inesperado al capturar evidencias reproducibles")
        return 2


def main() -> int:
    ruta_repo = _resolver_raiz_repo()
    return capturar_evidencias_reproducibles(ruta_repo)


if __name__ == "__main__":
    sys.exit(main())

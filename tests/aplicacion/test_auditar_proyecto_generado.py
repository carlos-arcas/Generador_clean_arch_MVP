from __future__ import annotations

import hashlib
import json

import pytest
from pathlib import Path

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.dtos.auditoria.dto_auditoria_entrada import DtoAuditoriaEntrada
from aplicacion.errores import ErrorAuditoria
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos, ResultadoProceso


class EjecutorFalso(EjecutorProcesos):
    def __init__(self, salida: str = "TOTAL 10 1 90%") -> None:
        self._salida = salida

    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return ResultadoProceso(0, self._salida, "")


class CalculadoraHashFalsa:
    def __init__(self, forzar_error: bool = False) -> None:
        self._forzar_error = forzar_error

    def calcular_hash_archivo(self, ruta: Path) -> str:
        if self._forzar_error:
            raise RuntimeError("hash no disponible")
        return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _crear_estructura_minima(base: Path) -> None:
    for carpeta in [
        "dominio",
        "aplicacion",
        "infraestructura",
        "presentacion",
        "tests",
        "scripts",
        "logs",
        "docs",
    ]:
        (base / carpeta).mkdir(parents=True, exist_ok=True)
    (base / "VERSION").write_text("1.0.0", encoding="utf-8")
    (base / "CHANGELOG.md").write_text("# cambios", encoding="utf-8")
    (base / "infraestructura" / "logging_config.py").write_text("", encoding="utf-8")
    (base / "logs" / "seguimiento.log").write_text("", encoding="utf-8")
    (base / "logs" / "crashes.log").write_text("", encoding="utf-8")


def test_auditar_proyecto_ok_con_hash_inyectado(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)
    archivo = tmp_path / "README.md"
    archivo.write_text("contenido", encoding="utf-8")
    hash_archivo = hashlib.sha256(archivo.read_bytes()).hexdigest()
    (tmp_path / "manifest.json").write_text(
        json.dumps({"archivos": [{"ruta_relativa": "README.md", "hash_sha256": hash_archivo}]}),
        encoding="utf-8",
    )

    resultado = AuditarProyectoGenerado(
        ejecutor_procesos=EjecutorFalso(),
        calculadora_hash=CalculadoraHashFalsa(),
    ).ejecutar(DtoAuditoriaEntrada(ruta_proyecto=str(tmp_path)))

    assert resultado.valido is True


def test_auditar_proyecto_error_si_falla_puerto_hash(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)
    archivo = tmp_path / "README.md"
    archivo.write_text("contenido", encoding="utf-8")
    (tmp_path / "manifest.json").write_text(
        json.dumps({"archivos": [{"ruta_relativa": "README.md", "hash_sha256": "abc"}]}),
        encoding="utf-8",
    )

    with pytest.raises(ErrorAuditoria, match="hash no disponible"):
        AuditarProyectoGenerado(
            ejecutor_procesos=EjecutorFalso(),
            calculadora_hash=CalculadoraHashFalsa(forzar_error=True),
        ).ejecutar(DtoAuditoriaEntrada(ruta_proyecto=str(tmp_path)))


def test_auditar_proyecto_limite_manifest_sin_archivos(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)
    (tmp_path / "manifest.json").write_text(json.dumps({"archivos": []}), encoding="utf-8")

    resultado = AuditarProyectoGenerado(
        ejecutor_procesos=EjecutorFalso(),
        calculadora_hash=CalculadoraHashFalsa(),
    ).ejecutar(DtoAuditoriaEntrada(ruta_proyecto=str(tmp_path)))

    assert resultado.valido is True

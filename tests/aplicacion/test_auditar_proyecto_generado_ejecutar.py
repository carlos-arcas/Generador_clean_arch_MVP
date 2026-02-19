from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.auditoria.validadores import ContextoAuditoria, ResultadoValidacion, ValidadorAuditoria
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos, ResultadoProceso


class EjecutorFalso(EjecutorProcesos):
    def __init__(self, codigo_salida: int = 0, salida: str = "TOTAL 10 1 90%") -> None:
        self._codigo_salida = codigo_salida
        self._salida = salida

    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return ResultadoProceso(self._codigo_salida, self._salida, "")


class ValidadorFalso(ValidadorAuditoria):
    def __init__(self, errores: list[str] | None = None) -> None:
        self._errores = errores or []

    def validar(self, contexto: ContextoAuditoria) -> ResultadoValidacion:
        return ResultadoValidacion(exito=not self._errores, errores=self._errores)


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


def test_ejecutar_happy_path_con_validadores_fakes(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)
    auditor = AuditarProyectoGenerado(ejecutor_procesos=EjecutorFalso())
    auditor._validadores_auditoria = [ValidadorFalso()]

    salida = auditor.ejecutar(str(tmp_path))

    assert salida.valido is True
    assert salida.lista_errores == []
    assert salida.cobertura == 90.0
    assert "Auditoría APROBADO" in salida.resumen


def test_ejecutar_refleja_severidad_con_error_de_validador(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)
    auditor = AuditarProyectoGenerado(ejecutor_procesos=EjecutorFalso())
    auditor._validadores_auditoria = [ValidadorFalso(["Error de arquitectura detectado"])]

    salida = auditor.ejecutar(str(tmp_path))

    assert salida.valido is False
    assert "Error de arquitectura detectado" in salida.lista_errores
    assert "Auditoría RECHAZADO" in salida.resumen


def test_ejecutar_sin_validadores(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)
    auditor = AuditarProyectoGenerado(ejecutor_procesos=EjecutorFalso())
    auditor._validadores_auditoria = []

    salida = auditor.ejecutar(str(tmp_path))

    assert salida.valido is True
    assert salida.lista_errores == []

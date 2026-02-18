from pathlib import Path

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos, ResultadoProceso


class EjecutorMock(EjecutorProcesos):
    def __init__(self, stdout: str, codigo: int = 0) -> None:
        self._stdout = stdout
        self._codigo = codigo

    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return ResultadoProceso(codigo_salida=self._codigo, stdout=self._stdout, stderr="")


def _crear_estructura_valida(base: Path) -> None:
    for carpeta in ["dominio", "aplicacion", "infraestructura", "presentacion", "tests", "scripts", "logs", "docs"]:
        (base / carpeta).mkdir(parents=True)
    (base / "VERSION").write_text("0.6.0", encoding="utf-8")
    (base / "CHANGELOG.md").write_text("# CHANGELOG", encoding="utf-8")
    (base / "infraestructura" / "logging_config.py").write_text("def configurar_logging(): pass", encoding="utf-8")
    (base / "logs" / "seguimiento.log").write_text("", encoding="utf-8")
    (base / "logs" / "crashes.log").write_text("", encoding="utf-8")


def test_auditor_cobertura_90_aprueba(tmp_path: Path) -> None:
    _crear_estructura_valida(tmp_path)

    resultado = AuditarProyectoGenerado(EjecutorMock("TOTAL 100 10 90%")).ejecutar(str(tmp_path))

    assert resultado.valido is True
    assert resultado.cobertura == 90.0


def test_auditor_cobertura_70_rechaza(tmp_path: Path) -> None:
    _crear_estructura_valida(tmp_path)

    resultado = AuditarProyectoGenerado(EjecutorMock("TOTAL 100 30 70%")).ejecutar(str(tmp_path))

    assert resultado.valido is False
    assert any("Cobertura insuficiente" in error for error in resultado.lista_errores)

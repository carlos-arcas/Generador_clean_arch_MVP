from pathlib import Path

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.dtos.auditoria.dto_auditoria_entrada import DtoAuditoriaEntrada
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos, ResultadoProceso


class EjecutorFalso(EjecutorProcesos):
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return ResultadoProceso(0, "TOTAL 10 1 90%", "")


def _crear_estructura_minima(base: Path) -> None:
    (base / "dominio").mkdir(parents=True)
    (base / "aplicacion").mkdir(parents=True)
    (base / "infraestructura").mkdir(parents=True)
    (base / "presentacion").mkdir(parents=True)
    (base / "tests").mkdir(parents=True)
    (base / "scripts").mkdir(parents=True)
    (base / "logs").mkdir(parents=True)
    (base / "docs").mkdir(parents=True)
    (base / "VERSION").write_text("0.2.0", encoding="utf-8")
    (base / "CHANGELOG.md").write_text("# CHANGELOG", encoding="utf-8")
    (base / "infraestructura" / "logging_config.py").write_text("def configurar_logging(): pass", encoding="utf-8")
    (base / "logs" / "seguimiento.log").write_text("", encoding="utf-8")
    (base / "logs" / "crashes.log").write_text("", encoding="utf-8")


def test_auditar_proyecto_valido(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)

    resultado = AuditarProyectoGenerado(EjecutorFalso()).ejecutar(DtoAuditoriaEntrada(ruta_proyecto=str(tmp_path)))

    assert resultado.valido is True
    assert resultado.errores == []


def test_auditar_proyecto_con_faltantes(tmp_path: Path) -> None:
    resultado = AuditarProyectoGenerado(EjecutorFalso()).ejecutar(DtoAuditoriaEntrada(ruta_proyecto=str(tmp_path)))

    assert resultado.valido is False
    assert len(resultado.errores) >= 10

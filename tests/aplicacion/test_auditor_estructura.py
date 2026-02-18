from pathlib import Path

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.dtos.auditoria.dto_auditoria_entrada import DtoAuditoriaEntrada
from aplicacion.puertos.calculadora_hash import CalculadoraHash
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos, ResultadoProceso


class EjecutorFalso(EjecutorProcesos):
    def __init__(self, resultado: ResultadoProceso) -> None:
        self._resultado = resultado

    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return self._resultado




class CalculadoraHashFalsa(CalculadoraHash):
    def calcular_sha256(self, ruta_absoluta: str) -> str:
        return "hash_falso"
def _crear_base_valida(base: Path) -> None:
    (base / "dominio").mkdir(parents=True)
    (base / "aplicacion").mkdir(parents=True)
    (base / "infraestructura").mkdir(parents=True)
    (base / "presentacion").mkdir(parents=True)
    (base / "tests").mkdir(parents=True)
    (base / "scripts").mkdir(parents=True)
    (base / "logs").mkdir(parents=True)
    (base / "docs").mkdir(parents=True)
    (base / "VERSION").write_text("0.7.0", encoding="utf-8")
    (base / "CHANGELOG.md").write_text("# CHANGELOG", encoding="utf-8")
    (base / "infraestructura" / "logging_config.py").write_text("def configurar_logging(): pass", encoding="utf-8")
    (base / "logs" / "seguimiento.log").write_text("", encoding="utf-8")
    (base / "logs" / "crashes.log").write_text("", encoding="utf-8")
    (base / "dominio" / "entidad.py").write_text("class Entidad: pass\n", encoding="utf-8")


def test_auditor_estructura_valida_crea_informe(tmp_path: Path) -> None:
    _crear_base_valida(tmp_path)
    ejecutor = EjecutorFalso(ResultadoProceso(0, "TOTAL 10 1 90%", ""))

    resultado = AuditarProyectoGenerado(ejecutor, CalculadoraHashFalsa()).ejecutar(DtoAuditoriaEntrada(ruta_proyecto=str(tmp_path), blueprints_usados=["base_clean_arch"]))

    assert resultado.valido is True
    assert resultado.cobertura == 90.0
    assert (tmp_path / "docs" / "informe_auditoria.md").exists()


def test_auditor_estructura_detecta_faltantes(tmp_path: Path) -> None:
    ejecutor = EjecutorFalso(ResultadoProceso(0, "TOTAL 10 1 90%", ""))

    resultado = AuditarProyectoGenerado(ejecutor, CalculadoraHashFalsa()).ejecutar(DtoAuditoriaEntrada(ruta_proyecto=str(tmp_path)))

    assert resultado.valido is False
    assert any("No existe el recurso obligatorio" in error for error in resultado.lista_errores)

from pathlib import Path

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.dtos.auditoria.dto_auditoria_entrada import DtoAuditoriaEntrada
from aplicacion.errores import ErrorAuditoria
from aplicacion.puertos.calculadora_hash import CalculadoraHash
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos, ResultadoProceso


class EjecutorProcesosDoble(EjecutorProcesos):
    def __init__(self, resultado: ResultadoProceso) -> None:
        self._resultado = resultado

    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return self._resultado


class CalculadoraHashDoble(CalculadoraHash):
    def __init__(self, valor: str = "hash", error: Exception | None = None) -> None:
        self._valor = valor
        self._error = error

    def calcular_sha256(self, ruta_absoluta: str) -> str:
        if self._error is not None:
            raise self._error
        return self._valor


def _crear_proyecto_minimo(base: Path) -> None:
    for carpeta in ["dominio", "aplicacion", "infraestructura", "presentacion", "tests", "scripts", "logs", "docs"]:
        (base / carpeta).mkdir(parents=True, exist_ok=True)
    (base / "VERSION").write_text("1.0.0", encoding="utf-8")
    (base / "CHANGELOG.md").write_text("# Changelog", encoding="utf-8")
    (base / "infraestructura" / "logging_config.py").write_text("def configurar_logging(): ...", encoding="utf-8")
    (base / "logs" / "seguimiento.log").write_text("", encoding="utf-8")
    (base / "logs" / "crashes.log").write_text("", encoding="utf-8")


def test_ejecutar_auditoria_valida(tmp_path: Path) -> None:
    _crear_proyecto_minimo(tmp_path)
    caso_uso = AuditarProyectoGenerado(
        ejecutor_procesos=EjecutorProcesosDoble(ResultadoProceso(codigo_salida=0, stdout="TOTAL 10 1 90%", stderr="")),
        calculadora_hash=CalculadoraHashDoble(),
    )

    salida = caso_uso.ejecutar(DtoAuditoriaEntrada(ruta_proyecto=str(tmp_path)))

    assert salida.valido is True
    assert salida.lista_errores == []
    assert salida.cobertura == 90.0


def test_ejecutar_auditoria_error_hash_lanza_error_auditoria(tmp_path: Path) -> None:
    _crear_proyecto_minimo(tmp_path)
    (tmp_path / "archivo.txt").write_text("contenido", encoding="utf-8")
    (tmp_path / "manifest.json").write_text(
        '{"archivos": [{"ruta_relativa": "archivo.txt", "hash_sha256": "esperado"}]}',
        encoding="utf-8",
    )
    caso_uso = AuditarProyectoGenerado(
        ejecutor_procesos=EjecutorProcesosDoble(ResultadoProceso(codigo_salida=0, stdout="TOTAL 10 1 90%", stderr="")),
        calculadora_hash=CalculadoraHashDoble(error=RuntimeError("falla hash")),
    )

    try:
        caso_uso.ejecutar(DtoAuditoriaEntrada(ruta_proyecto=str(tmp_path)))
        assert False, "Se esperaba ErrorAuditoria"
    except ErrorAuditoria as error:
        assert "falla hash" in str(error)


def test_ejecutar_auditoria_limite_proyecto_vacio(tmp_path: Path) -> None:
    caso_uso = AuditarProyectoGenerado(
        ejecutor_procesos=EjecutorProcesosDoble(ResultadoProceso(codigo_salida=0, stdout="TOTAL 10 1 90%", stderr="")),
        calculadora_hash=CalculadoraHashDoble(),
    )

    salida = caso_uso.ejecutar(DtoAuditoriaEntrada(ruta_proyecto=str(tmp_path)))

    assert salida.valido is False
    assert any("No existe el recurso obligatorio" in error for error in salida.lista_errores)

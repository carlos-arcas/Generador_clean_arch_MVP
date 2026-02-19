import ast
import inspect
import textwrap
from pathlib import Path

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.auditoria.validadores import ContextoAuditoria, ResultadoValidacion, ValidadorAuditoria
from aplicacion.casos_uso.auditoria.validadores.validador_imports import ValidadorImports
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos, ResultadoProceso


class EjecutorFalso(EjecutorProcesos):
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return ResultadoProceso(0, "TOTAL 10 1 90%", "")


class ValidadorDoble(ValidadorAuditoria):
    def __init__(self) -> None:
        self.ejecutado = False

    def validar(self, contexto: ContextoAuditoria) -> ResultadoValidacion:
        self.ejecutado = True
        return ResultadoValidacion(exito=True, errores=[])


def _crear_estructura_minima(base: Path) -> None:
    for carpeta in ["dominio", "aplicacion", "infraestructura", "presentacion", "tests", "scripts", "logs", "docs"]:
        (base / carpeta).mkdir(parents=True)
    (base / "VERSION").write_text("1.0.0", encoding="utf-8")
    (base / "CHANGELOG.md").write_text("# CHANGELOG", encoding="utf-8")
    (base / "infraestructura" / "logging_config.py").write_text("def configurar_logging(): pass", encoding="utf-8")
    (base / "logs" / "seguimiento.log").write_text("", encoding="utf-8")
    (base / "logs" / "crashes.log").write_text("", encoding="utf-8")


def test_validador_imports_caso_correcto(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)
    (tmp_path / "presentacion" / "vista.py").write_text("from aplicacion.servicio import Servicio\n", encoding="utf-8")

    resultado = ValidadorImports().validar(ContextoAuditoria(base=tmp_path))

    assert resultado.exito is True
    assert resultado.errores == []


def test_validador_imports_detecta_presentacion_hacia_dominio(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)
    (tmp_path / "presentacion" / "vista.py").write_text("from dominio.entidad import Entidad\n", encoding="utf-8")
    (tmp_path / "dominio" / "entidad.py").write_text("class Entidad: pass\n", encoding="utf-8")

    resultado = ValidadorImports().validar(ContextoAuditoria(base=tmp_path))

    assert resultado.exito is False
    assert any("Import prohibido en presentación" in error for error in resultado.errores)


def test_validador_imports_detecta_aplicacion_hacia_infraestructura(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)
    (tmp_path / "aplicacion" / "caso.py").write_text("from infraestructura.repo import Repo\n", encoding="utf-8")
    (tmp_path / "infraestructura" / "repo.py").write_text("class Repo: pass\n", encoding="utf-8")

    resultado = ValidadorImports().validar(ContextoAuditoria(base=tmp_path))

    assert resultado.exito is False
    assert any("Import prohibido en aplicación" in error for error in resultado.errores)


def test_validador_imports_detecta_dominio_hacia_otras_capas(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)
    (tmp_path / "dominio" / "entidad.py").write_text("from presentacion.ui import Pantalla\n", encoding="utf-8")

    resultado = ValidadorImports().validar(ContextoAuditoria(base=tmp_path))

    assert resultado.exito is False
    assert any("Import prohibido en dominio" in error for error in resultado.errores)


def test_validador_imports_proyecto_vacio(tmp_path: Path) -> None:
    resultado = ValidadorImports().validar(ContextoAuditoria(base=tmp_path))

    assert resultado.exito is True
    assert resultado.errores == []


def test_regla_imports_dominio_reducida_en_complejidad() -> None:
    codigo = textwrap.dedent(inspect.getsource(ValidadorImports._regla_imports_dominio))
    arbol = ast.parse(codigo)
    nodos_if = [nodo for nodo in ast.walk(arbol) if isinstance(nodo, ast.If)]

    assert len(nodos_if) <= 2


def test_auditar_proyecto_incluye_validador_imports_en_pipeline(tmp_path: Path) -> None:
    _crear_estructura_minima(tmp_path)
    doble = ValidadorDoble()
    auditor = AuditarProyectoGenerado(EjecutorFalso())
    auditor._validadores_auditoria = [doble]

    resultado = auditor.ejecutar(str(tmp_path))

    assert doble.ejecutado is True
    assert resultado.valido is True

from __future__ import annotations

from pathlib import Path

import pytest

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.construir_especificacion_proyecto import ConstruirEspecificacionProyecto
from aplicacion.dtos.proyecto import DtoAtributo, DtoClase, DtoProyectoEntrada
from aplicacion.errores import ErrorValidacion
from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos, ResultadoProceso
from aplicacion.validacion import MotorValidacion, ReglaValidacion, ResultadoValidacion


class _ReglaMarca(ReglaValidacion):
    def __init__(self, marca: str) -> None:
        self.marca = marca

    def validar(self, contexto: list[str]) -> ResultadoValidacion | None:
        contexto.append(self.marca)
        return ResultadoValidacion(True, None, "INFO")


class _ReglaError(ReglaValidacion):
    def validar(self, contexto: object) -> ResultadoValidacion | None:
        return ResultadoValidacion(False, "Error de prueba", "ERROR")


class _ReglaOk(ReglaValidacion):
    def validar(self, contexto: object) -> ResultadoValidacion | None:
        return None


class _EjecutorExitoso(EjecutorProcesos):
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return ResultadoProceso(0, "TOTAL 10 0 100%", "")


def _crear_proyecto_minimo(base: Path) -> None:
    for carpeta in ["dominio", "aplicacion", "infraestructura", "presentacion", "tests", "scripts", "logs", "docs"]:
        (base / carpeta).mkdir(parents=True, exist_ok=True)
    (base / "VERSION").write_text("0.1.0", encoding="utf-8")
    (base / "CHANGELOG.md").write_text("# cambios", encoding="utf-8")
    (base / "infraestructura" / "logging_config.py").write_text("", encoding="utf-8")
    (base / "logs" / "seguimiento.log").write_text("", encoding="utf-8")
    (base / "logs" / "crashes.log").write_text("", encoding="utf-8")


def test_motor_ejecuta_multiples_reglas() -> None:
    contexto: list[str] = []
    resultados = MotorValidacion([_ReglaMarca("a"), _ReglaMarca("b")]).ejecutar(contexto)

    assert contexto == ["a", "b"]
    assert len(resultados) == 2


def test_regla_fallida_devuelve_error() -> None:
    resultados = MotorValidacion([_ReglaError()]).ejecutar({})

    assert resultados[0].severidad == "ERROR"
    assert resultados[0].exito is False


def test_regla_ok_no_agrega_error() -> None:
    resultados = MotorValidacion([_ReglaOk()]).ejecutar({})

    assert resultados == []


def test_integracion_basica_auditoria_con_motor(tmp_path: Path) -> None:
    _crear_proyecto_minimo(tmp_path)

    resultado = AuditarProyectoGenerado(_EjecutorExitoso()).ejecutar(str(tmp_path))

    assert resultado.valido is True
    assert resultado.lista_errores == []


def test_integracion_basica_validacion_dto_con_motor() -> None:
    dto = DtoProyectoEntrada(
        nombre_proyecto="",
        ruta_destino="/tmp/demo",
        clases=[DtoClase(nombre="Entidad", atributos=[DtoAtributo(nombre="id", tipo="int")])],
    )

    with pytest.raises(ErrorValidacion, match="nombre del proyecto"):
        ConstruirEspecificacionProyecto().ejecutar(dto)

class _EjecutorSinCobertura(EjecutorProcesos):
    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        return ResultadoProceso(1, "sin datos", "fallo")


def test_auditoria_reporta_dependencias_faltantes_para_informes(tmp_path: Path) -> None:
    _crear_proyecto_minimo(tmp_path)
    (tmp_path / "requirements.txt").write_text("openpyxl==3.1.0", encoding="utf-8")

    resultado = AuditarProyectoGenerado(_EjecutorExitoso()).ejecutar(str(tmp_path), ["export_pdf"])

    assert resultado.valido is False
    assert any("reportlab" in error for error in resultado.lista_errores)


def test_auditoria_reporta_manifest_invalido(tmp_path: Path) -> None:
    _crear_proyecto_minimo(tmp_path)
    (tmp_path / "manifest.json").write_text('{"archivos": [{"ruta_relativa": "", "hash_sha256": ""}]}', encoding="utf-8")

    resultado = AuditarProyectoGenerado(_EjecutorExitoso()).ejecutar(str(tmp_path))

    assert any("entradas incompletas" in error for error in resultado.lista_errores)


def test_auditoria_reporta_error_si_pytest_falla_sin_cobertura(tmp_path: Path) -> None:
    _crear_proyecto_minimo(tmp_path)

    resultado = AuditarProyectoGenerado(_EjecutorSinCobertura()).ejecutar(str(tmp_path))

    assert resultado.valido is False
    assert any("sin reporte de cobertura usable" in error for error in resultado.lista_errores)

from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_base import ReglaDependencia
from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_no_imports_circulares import (
    ReglaNoImportsCirculares,
)
from aplicacion.casos_uso.auditoria.validadores.validador_base import ContextoAuditoria


def test_regla_base_es_abstracta_y_define_evaluar() -> None:
    assert hasattr(ReglaDependencia, "evaluar")
    assert ReglaDependencia.__abstractmethods__ == frozenset({"evaluar"})


def test_regla_no_imports_circulares_devuelve_resultado_ok() -> None:
    contexto = ContextoAuditoria(base=Path("."))

    resultado = ReglaNoImportsCirculares().evaluar(contexto)

    assert resultado.exito is True
    assert resultado.errores == []

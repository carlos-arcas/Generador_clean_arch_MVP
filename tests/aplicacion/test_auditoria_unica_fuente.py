from __future__ import annotations

from importlib import import_module
from pathlib import Path

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria


def test_modulo_raiz_es_puente_y_fuente_unica_en_submodulo() -> None:
    modulo_puente = import_module("aplicacion.casos_uso.auditar_proyecto_generado")
    modulo_fuente = import_module("aplicacion.casos_uso.auditoria.auditar_proyecto_generado")

    contenido_puente = Path(modulo_puente.__file__).read_text(encoding="utf-8")

    assert "from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import *" in contenido_puente
    assert modulo_puente.AuditarProyectoGenerado.__module__ == modulo_fuente.__name__


def test_resultado_auditoria_alias_errores_funciona() -> None:
    resultado = ResultadoAuditoria(valido=False, lista_errores=["error de prueba"], cobertura=90.0)

    assert resultado.valido is False
    assert resultado.errores == ["error de prueba"]
    assert resultado.lista_errores == ["error de prueba"]
    assert resultado.cobertura == 90.0

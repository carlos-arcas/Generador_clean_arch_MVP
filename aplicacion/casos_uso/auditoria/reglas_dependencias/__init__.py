"""Reglas de dependencias entre capas para auditoría.

El módulo mantiene una API pública estable sin importar todas las reglas en tiempo de
carga. Esto evita imports adelantados innecesarios desde ``__init__`` y conserva
``from ...reglas_dependencias import X`` mediante resolución diferida.
"""

from __future__ import annotations

from importlib import import_module

__all__ = [
    "ReglaDependencia",
    "ReglaPresentacionNoDependeDominio",
    "ReglaAplicacionNoDependeInfraestructura",
    "ReglaDominioNoDependeDeOtrasCapas",
    "ReglaNoImportsCirculares",
]

_EXPORTS = {
    "ReglaDependencia": "regla_base",
    "ReglaPresentacionNoDependeDominio": "regla_presentacion_no_depende_dominio",
    "ReglaAplicacionNoDependeInfraestructura": "regla_aplicacion_no_depende_infraestructura",
    "ReglaDominioNoDependeDeOtrasCapas": "regla_dominio_no_depende_de_otras_capas",
    "ReglaNoImportsCirculares": "regla_no_imports_circulares",
}


def __getattr__(nombre: str) -> object:
    modulo_relativo = _EXPORTS.get(nombre)
    if modulo_relativo is None:
        raise AttributeError(f"module {__name__!r} has no attribute {nombre!r}")

    modulo = import_module(f".{modulo_relativo}", package=__name__)
    return getattr(modulo, nombre)

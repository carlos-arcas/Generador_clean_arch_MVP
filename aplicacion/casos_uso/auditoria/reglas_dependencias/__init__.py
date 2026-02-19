"""Reglas de dependencias entre capas para auditoría."""

from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_aplicacion_no_depende_infraestructura import (
    ReglaAplicacionNoDependeInfraestructura,
)
from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_base import ReglaDependencia
from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_dominio_no_depende_de_otras_capas import (
    ReglaDominioNoDependeDeOtrasCapas,
)
from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_no_imports_circulares import (
    ReglaNoImportsCirculares,
)
from aplicacion.casos_uso.auditoria.reglas_dependencias.regla_presentacion_no_depende_dominio import (
    ReglaPresentacionNoDependeDominio,
)

__all__ = [
    "ReglaDependencia",
    "ReglaPresentacionNoDependeDominio",
    "ReglaAplicacionNoDependeInfraestructura",
    "ReglaDominioNoDependeDeOtrasCapas",
    "ReglaNoImportsCirculares",
]

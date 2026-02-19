from __future__ import annotations

from aplicacion.casos_uso.auditar_finalizacion_proyecto import AuditarFinalizacionProyecto
from aplicacion.dtos.auditoria import CONFLICTO, INESPERADO, IO, VALIDACION
from aplicacion.errores import ErrorConflictoArchivos
from dominio.errores import ErrorValidacionDominio


class _Dummy:
    def ejecutar(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise NotImplementedError

    def auditar(self, ruta_proyecto: str):  # type: ignore[no-untyped-def]
        raise NotImplementedError


def _caso() -> AuditarFinalizacionProyecto:
    return AuditarFinalizacionProyecto(_Dummy(), _Dummy(), _Dummy(), _Dummy())


def test_clasifica_error_validacion_dominio() -> None:
    assert _caso()._clasificar_fallo(ErrorValidacionDominio("x")) == VALIDACION


def test_clasifica_error_conflicto_archivos() -> None:
    assert _caso()._clasificar_fallo(ErrorConflictoArchivos("x")) == CONFLICTO


def test_clasifica_error_oserror() -> None:
    assert _caso()._clasificar_fallo(OSError("x")) == IO


def test_clasifica_exception_generica() -> None:
    assert _caso()._clasificar_fallo(Exception("x")) == INESPERADO

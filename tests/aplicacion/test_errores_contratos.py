from __future__ import annotations

from aplicacion.errores.errores_auditoria import ErrorAuditoria
from aplicacion.errores.errores_generacion import (
    ErrorBlueprintNoEncontrado,
    ErrorConflictoArchivos,
    ErrorGeneracionProyecto,
    ErrorInfraestructura,
)
from aplicacion.errores.errores_pipeline import (
    ErrorAuditoriaGeneracion,
    ErrorEjecucionPlanGeneracion,
    ErrorNormalizacionEntradaGeneracion,
    ErrorPreparacionEstructuraGeneracion,
    ErrorPublicacionManifestGeneracion,
    ErrorValidacionEntradaGeneracion,
)
from aplicacion.errores.errores_validacion import ErrorAplicacion, ErrorValidacion, ErrorValidacionEntrada


def test_errores_aplicacion_heredan_exception() -> None:
    for error in [
        ErrorAplicacion,
        ErrorValidacionEntrada,
        ErrorValidacion,
        ErrorGeneracionProyecto,
        ErrorConflictoArchivos,
        ErrorBlueprintNoEncontrado,
        ErrorInfraestructura,
        ErrorValidacionEntradaGeneracion,
        ErrorNormalizacionEntradaGeneracion,
        ErrorPreparacionEstructuraGeneracion,
        ErrorEjecucionPlanGeneracion,
        ErrorPublicacionManifestGeneracion,
        ErrorAuditoriaGeneracion,
        ErrorAuditoria,
    ]:
        assert issubclass(error, Exception)


def test_errores_conservan_mensaje_al_instanciar() -> None:
    mensaje = "fallo-controlado"

    assert str(ErrorGeneracionProyecto(mensaje)) == mensaje
    assert str(ErrorAuditoriaGeneracion(mensaje)) == mensaje
    assert str(ErrorAuditoria(mensaje)) == mensaje

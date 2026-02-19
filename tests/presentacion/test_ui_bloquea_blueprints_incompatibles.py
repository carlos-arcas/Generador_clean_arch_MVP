from __future__ import annotations

from aplicacion.casos_uso.validar_compatibilidad_blueprints import ValidarCompatibilidadBlueprints
from infraestructura.blueprints.metadata_registry import obtener_metadata_blueprints
from presentacion.wizard.dtos import DatosWizardProyecto
from presentacion.wizard.orquestadores.orquestador_finalizacion_wizard import (
    DtoEntradaFinalizacionWizard,
    OrquestadorFinalizacionWizard,
)


class ProyectoFalso:
    def __init__(self) -> None:
        self.clases = [object()]


class LanzadorDoble:
    def __init__(self) -> None:
        self.llamadas = 0

    def __call__(self, entrada):  # noqa: ANN001
        self.llamadas += 1


def test_no_lanza_generacion_si_hay_conflicto_declarativo() -> None:
    lanzador = LanzadorDoble()
    orquestador = OrquestadorFinalizacionWizard(
        validador_final=lambda proyecto: proyecto,
        lanzador_generacion=lanzador,
        validador_compatibilidad_blueprints=ValidarCompatibilidadBlueprints(obtener_metadata_blueprints()),
    )
    datos = DatosWizardProyecto(
        nombre="Demo",
        ruta="/tmp",
        descripcion="",
        version="1.0.0",
        proyecto=ProyectoFalso(),
        persistencia="JSON",
    )

    resultado = orquestador.finalizar(
        DtoEntradaFinalizacionWizard(datos_wizard=datos, blueprints=["crud_json", "crud_sqlite"])
    )

    assert resultado.exito is False
    assert lanzador.llamadas == 0
    assert resultado.detalles is not None
    assert "conflictos_declarativos" in resultado.detalles

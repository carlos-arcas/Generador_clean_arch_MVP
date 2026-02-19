from __future__ import annotations

import copy
from pathlib import Path

from dominio.modelos import EspecificacionProyecto
from presentacion.wizard.dtos import DatosWizardProyecto
from presentacion.wizard.orquestadores.orquestador_finalizacion_wizard import (
    DtoEntradaFinalizacionWizard,
    OrquestadorFinalizacionWizard,
)


def test_wizard_orquestador_preserva_dto_y_no_imprime(capsys) -> None:
    proyecto = EspecificacionProyecto(nombre_proyecto="demo", ruta_destino="/tmp/demo")
    datos = DatosWizardProyecto(
        nombre="demo",
        ruta="/tmp/demo",
        descripcion="",
        version="1.0.0",
        proyecto=proyecto,
        persistencia="JSON",
    )
    dto = DtoEntradaFinalizacionWizard(datos_wizard=datos, blueprints=["base_clean_arch_v1"])
    dto_original = copy.deepcopy(dto)

    entradas = []
    orquestador = OrquestadorFinalizacionWizard(
        validador_final=lambda p: p,
        lanzador_generacion=lambda entrada: entradas.append(entrada),
    )

    salida = orquestador.finalizar(dto)
    captured = capsys.readouterr()

    assert salida.exito is True
    assert entradas and entradas[0].blueprints == ["base_clean_arch_v1"]
    assert dto == dto_original
    assert captured.out == ""
    assert captured.err == ""

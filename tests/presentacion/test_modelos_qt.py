"""Pruebas unitarias para modelos Qt de presentación."""

from __future__ import annotations

import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtCore = pytest.importorskip("PySide6.QtCore", exc_type=ImportError)
Qt = QtCore.Qt

from presentacion.dtos import DtoVistaAtributo, DtoVistaClase
from presentacion.modelos_qt.modelo_atributos import ModeloAtributos
from presentacion.modelos_qt.modelo_clases import ModeloClases


def test_modelo_clases_expone_datos_y_encabezados() -> None:
    clase = DtoVistaClase(
        nombre="Cliente",
        atributos=[DtoVistaAtributo(nombre="nombre", tipo="str", obligatorio=True)],
    )
    modelo = ModeloClases([clase])

    assert modelo.rowCount() == 1
    assert modelo.columnCount() == 2
    assert modelo.data(modelo.index(0, 0), Qt.DisplayRole) == "Cliente"
    assert modelo.data(modelo.index(0, 1), Qt.DisplayRole) == "1"
    assert modelo.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "Nombre"
    assert modelo.clase_en_fila(0) == clase
    assert modelo.clase_en_fila(99) is None


def test_modelo_atributos_expone_datos_y_actualiza() -> None:
    atributo = DtoVistaAtributo(
        nombre="edad",
        tipo="int",
        obligatorio=False,
        valor_por_defecto="18",
    )
    modelo = ModeloAtributos([atributo])

    assert modelo.rowCount() == 1
    assert modelo.columnCount() == 4
    assert modelo.data(modelo.index(0, 0), Qt.DisplayRole) == "edad"
    assert modelo.data(modelo.index(0, 1), Qt.DisplayRole) == "int"
    assert modelo.data(modelo.index(0, 2), Qt.DisplayRole) == "No"
    assert modelo.data(modelo.index(0, 3), Qt.DisplayRole) == "18"
    assert modelo.headerData(2, Qt.Horizontal, Qt.DisplayRole) == "Obligatorio"
    assert modelo.atributo_en_fila(0) == atributo
    assert modelo.atributo_en_fila(-1) is None

    modelo.actualizar([])
    assert modelo.rowCount() == 0

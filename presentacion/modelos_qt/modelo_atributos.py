"""Modelo Qt de solo lectura para visualizar atributos de una clase seleccionada."""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from aplicacion.dtos_presentacion import DtoAtributoPresentacion


class ModeloAtributos(QAbstractTableModel):
    """Expone una lista de ``DtoAtributoPresentacion`` en una tabla Qt."""

    ENCABEZADOS = ["Nombre", "Tipo", "Obligatorio", "Valor por defecto"]

    def __init__(self, atributos: list[DtoAtributoPresentacion] | None = None) -> None:
        super().__init__()
        self._atributos = atributos or []

    def actualizar(self, atributos: list[DtoAtributoPresentacion]) -> None:
        self.beginResetModel()
        self._atributos = atributos
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._atributos)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self.ENCABEZADOS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str | None:
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        atributo = self._atributos[index.row()]
        if index.column() == 0:
            return atributo.nombre
        if index.column() == 1:
            return atributo.tipo
        if index.column() == 2:
            return "Sí" if atributo.obligatorio else "No"
        if index.column() == 3:
            return atributo.valor_por_defecto or ""
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> str | None:  # noqa: N802
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.ENCABEZADOS[section]
        return str(section + 1)

    def atributo_en_fila(self, fila: int) -> DtoAtributoPresentacion | None:
        if fila < 0 or fila >= len(self._atributos):
            return None
        return self._atributos[fila]

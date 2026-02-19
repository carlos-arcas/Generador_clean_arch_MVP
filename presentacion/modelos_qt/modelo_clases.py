"""Modelo Qt de solo lectura para visualizar clases de la especificación."""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from aplicacion.dtos_presentacion import DtoClasePresentacion


class ModeloClases(QAbstractTableModel):
    """Expone una lista de ``DtoClasePresentacion`` en una tabla Qt."""

    ENCABEZADOS = ["Nombre", "Cantidad atributos"]

    def __init__(self, clases: list[DtoClasePresentacion] | None = None) -> None:
        super().__init__()
        self._clases = clases or []

    def actualizar(self, clases: list[DtoClasePresentacion]) -> None:
        self.beginResetModel()
        self._clases = clases
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._clases)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self.ENCABEZADOS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> str | None:
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        clase = self._clases[index.row()]
        if index.column() == 0:
            return clase.nombre
        if index.column() == 1:
            return str(len(clase.atributos))
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

    def clase_en_fila(self, fila: int) -> DtoClasePresentacion | None:
        if fila < 0 or fila >= len(self._clases):
            return None
        return self._clases[fila]

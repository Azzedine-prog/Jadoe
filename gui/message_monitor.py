"""Message monitor table view."""
from __future__ import annotations

from typing import Callable, List, Optional

from PySide6 import QtCore, QtWidgets

from core.models import RxEntry


class MessageMonitor(QtWidgets.QTableWidget):
    selection_changed = QtCore.Signal(int)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "Time",
            "ID (hex)",
            "ID (dec)",
            "Name",
            "DLC",
            "Data",
            "Decoded",
        ])
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self._entries: List[RxEntry] = []
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def update_entries(self, entries: List[RxEntry]) -> None:
        self._entries = entries
        self.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            self._set_row(row, entry)

    def _set_row(self, row: int, entry: RxEntry) -> None:
        self.setItem(row, 0, QtWidgets.QTableWidgetItem(f"{entry.timestamp:.3f}"))
        self.setItem(row, 1, QtWidgets.QTableWidgetItem(hex(entry.arbitration_id)))
        self.setItem(row, 2, QtWidgets.QTableWidgetItem(str(entry.arbitration_id)))
        self.setItem(row, 3, QtWidgets.QTableWidgetItem(entry.message_name or ""))
        self.setItem(row, 4, QtWidgets.QTableWidgetItem(str(entry.dlc)))
        self.setItem(row, 5, QtWidgets.QTableWidgetItem(entry.data_hex))
        decoded = "; ".join(f"{k}={v}" for k, v in entry.decoded.items())
        self.setItem(row, 6, QtWidgets.QTableWidgetItem(decoded))

    def _on_selection_changed(self) -> None:
        rows = self.selectionModel().selectedRows()
        if not rows:
            return
        index = rows[0].row()
        self.selection_changed.emit(index)

    def current_entry(self) -> Optional[RxEntry]:
        rows = self.selectionModel().selectedRows()
        if not rows:
            return None
        return self._entries[rows[0].row()]

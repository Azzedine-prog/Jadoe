"""Signal detail dock widget."""
from __future__ import annotations

from typing import Dict, Optional

from PySide6 import QtWidgets


class SignalView(QtWidgets.QTableWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            "Signal",
            "Phys",
            "Raw",
            "Unit",
            "Range",
        ])
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)

    def update_signals(self, signals: Dict[str, Dict[str, str]]) -> None:
        self.setRowCount(len(signals))
        for row, (name, meta) in enumerate(signals.items()):
            self.setItem(row, 0, QtWidgets.QTableWidgetItem(name))
            self.setItem(row, 1, QtWidgets.QTableWidgetItem(str(meta.get("phys"))))
            self.setItem(row, 2, QtWidgets.QTableWidgetItem(str(meta.get("raw"))))
            self.setItem(row, 3, QtWidgets.QTableWidgetItem(meta.get("unit", "")))
            self.setItem(row, 4, QtWidgets.QTableWidgetItem(meta.get("range", "")))

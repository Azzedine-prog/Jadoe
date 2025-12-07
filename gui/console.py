"""Simple console widget for logs."""
from __future__ import annotations

from typing import Optional

from PySide6 import QtWidgets


class ConsoleWidget(QtWidgets.QTextEdit):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Log output will appear here")

    def log(self, text: str) -> None:
        self.append(text)

"""Entry point for Jadoe CAN Studio."""
from __future__ import annotations

import sys

from PySide6 import QtWidgets

from app.controller import ApplicationController
from core.config import WorkspaceSettings
from gui.main_window import MainWindow
from gui.theme import ThemeManager


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Jadoe CAN Studio")

    theme_manager = ThemeManager()
    theme_manager.apply(app)

    window = MainWindow()
    window.theme_manager = theme_manager  # type: ignore[attr-defined]

    settings = WorkspaceSettings.load()
    controller = ApplicationController(window, settings, theme_manager)

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

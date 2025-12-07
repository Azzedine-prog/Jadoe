"""Theme manager providing dark/light palettes and stylesheets."""
from __future__ import annotations

from PySide6 import QtGui


class ThemeManager:
    """Centralized theme information for the application."""

    def __init__(self) -> None:
        self.dark_palette = self._build_dark_palette()
        self.light_palette = self._build_light_palette()
        self.dark_stylesheet = self._build_dark_stylesheet()
        self.light_stylesheet = self._build_light_stylesheet()
        self.dark = True

    def apply(self, app: "QtWidgets.QApplication") -> None:
        palette = self.dark_palette if self.dark else self.light_palette
        stylesheet = self.dark_stylesheet if self.dark else self.light_stylesheet
        app.setPalette(palette)
        app.setStyleSheet(stylesheet)

    def toggle(self, app: "QtWidgets.QApplication") -> None:
        self.dark = not self.dark
        self.apply(app)

    @staticmethod
    def _build_dark_palette() -> QtGui.QPalette:
        palette = QtGui.QPalette()
        background = QtGui.QColor("#121212")
        surface = QtGui.QColor("#1E1E1E")
        text = QtGui.QColor("#E0E0E0")
        accent = QtGui.QColor("#3DA5D9")
        palette.setColor(QtGui.QPalette.Window, background)
        palette.setColor(QtGui.QPalette.Base, surface)
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#222"))
        palette.setColor(QtGui.QPalette.Text, text)
        palette.setColor(QtGui.QPalette.WindowText, text)
        palette.setColor(QtGui.QPalette.Button, surface)
        palette.setColor(QtGui.QPalette.ButtonText, text)
        palette.setColor(QtGui.QPalette.Highlight, accent)
        return palette

    @staticmethod
    def _build_light_palette() -> QtGui.QPalette:
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#FAFAFA"))
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor("#FFFFFF"))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#F1F1F1"))
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor("#1A1A1A"))
        palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#1A1A1A"))
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor("#F1F1F1"))
        palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#1A1A1A"))
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#2C7BE5"))
        return palette

    @staticmethod
    def _build_dark_stylesheet() -> str:
        return """
            QWidget { background-color: #1E1E1E; color: #E0E0E0; }
            QTableView { alternate-background-color: #242424; gridline-color: #333; }
            QHeaderView::section { background-color: #232323; padding: 6px; border: 0px; border-bottom: 1px solid #333; }
            QLineEdit, QComboBox, QSpinBox, QTextEdit { background: #242424; border: 1px solid #2E2E2E; border-radius: 4px; padding: 4px; }
            QPushButton { background-color: #2A2A2A; border: 1px solid #3DA5D9; border-radius: 6px; padding: 6px 12px; }
            QPushButton:hover { background-color: #2F2F2F; }
            QPushButton:pressed { background-color: #255C7D; }
            QToolBar { background: #1B1B1B; border: 0px; }
            QStatusBar { background: #1B1B1B; }
        """

    @staticmethod
    def _build_light_stylesheet() -> str:
        return """
            QWidget { background-color: #FAFAFA; color: #1A1A1A; }
            QTableView { alternate-background-color: #F3F3F3; gridline-color: #DDD; }
            QHeaderView::section { background-color: #F0F0F0; padding: 6px; border: 0px; border-bottom: 1px solid #DDD; }
            QLineEdit, QComboBox, QSpinBox, QTextEdit { background: #FFFFFF; border: 1px solid #D0D0D0; border-radius: 4px; padding: 4px; }
            QPushButton { background-color: #E9ECEF; border: 1px solid #2C7BE5; border-radius: 6px; padding: 6px 12px; }
            QPushButton:hover { background-color: #DEE2E6; }
            QPushButton:pressed { background-color: #B0C4FF; }
            QToolBar { background: #F0F0F0; border: 0px; }
            QStatusBar { background: #F0F0F0; }
        """

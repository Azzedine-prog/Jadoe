"""Main application window layout."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from PySide6 import QtCore, QtGui, QtWidgets

from core.models import RxEntry, TxMessageModel
from gui.console import ConsoleWidget
from gui.message_monitor import MessageMonitor
from gui.signal_view import SignalView
from gui.transmit_panel import TransmitPanel


class MainWindow(QtWidgets.QMainWindow):
    load_dbc_requested = QtCore.Signal()
    unload_dbc_requested = QtCore.Signal()
    connect_requested = QtCore.Signal()
    disconnect_requested = QtCore.Signal()
    start_logging_requested = QtCore.Signal()
    stop_logging_requested = QtCore.Signal()
    start_replay_requested = QtCore.Signal()
    stop_replay_requested = QtCore.Signal()
    theme_toggle_requested = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jadoe CAN Studio")
        self.resize(1200, 800)

        self.monitor = MessageMonitor()
        self.signal_view = SignalView()
        self.tx_panel = TransmitPanel()
        self.console = ConsoleWidget()

        self._build_ui()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.addWidget(self.monitor)
        self.setCentralWidget(central)

        signal_dock = QtWidgets.QDockWidget("Signals", self)
        signal_dock.setWidget(self.signal_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, signal_dock)

        tx_dock = QtWidgets.QDockWidget("Transmit", self)
        tx_dock.setWidget(self.tx_panel)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, tx_dock)

        console_dock = QtWidgets.QDockWidget("Console", self)
        console_dock.setWidget(self.console)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, console_dock)

        self._build_toolbar()
        self._build_statusbar()

    def _build_toolbar(self) -> None:
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        actions = {
            "Open DBC": ("ctrl+o", self.load_dbc_requested),
            "Unload DBC": ("ctrl+shift+o", self.unload_dbc_requested),
            "Connect": ("ctrl+c", self.connect_requested),
            "Disconnect": ("ctrl+d", self.disconnect_requested),
            "Start Logging": ("ctrl+l", self.start_logging_requested),
            "Stop Logging": ("ctrl+shift+l", self.stop_logging_requested),
            "Start Replay": ("ctrl+r", self.start_replay_requested),
            "Stop Replay": ("ctrl+shift+r", self.stop_replay_requested),
            "Toggle Theme": ("ctrl+t", self.theme_toggle_requested),
        }
        for text, (shortcut, signal) in actions.items():
            action = QtGui.QAction(text, self)
            action.setShortcut(shortcut)
            action.triggered.connect(signal.emit)
            toolbar.addAction(action)

    def _build_statusbar(self) -> None:
        self.status_messages = QtWidgets.QLabel("Disconnected")
        self.status_rx_count = QtWidgets.QLabel("Rx: 0")
        self.status_logging = QtWidgets.QLabel("Logging: stopped")
        bar = self.statusBar()
        bar.addPermanentWidget(self.status_messages)
        bar.addPermanentWidget(self.status_rx_count)
        bar.addPermanentWidget(self.status_logging)

    def update_rx(self, entries: Dict[str, RxEntry]) -> None:
        self.monitor.update_entries(list(entries.values()))
        self.status_rx_count.setText(f"Rx: {len(entries)}")

    def update_signals(self, signals: Dict[str, Dict[str, str]]) -> None:
        self.signal_view.update_signals(signals)

    def set_tx_models(self, models: Dict[str, TxMessageModel]) -> None:
        self.tx_panel.set_messages(models)
        self.tx_panel.connect_signals()

    def log_message(self, text: str) -> None:
        self.console.log(text)

    def set_connection_status(self, connected: bool) -> None:
        self.status_messages.setText("Connected" if connected else "Disconnected")

    def set_logging_status(self, active: bool, path: Optional[Path] = None) -> None:
        label = "Logging: active" if active else "Logging: stopped"
        if active and path:
            label += f" ({path.name})"
        self.status_logging.setText(label)

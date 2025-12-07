"""Main application window layout."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from PySide6 import QtCore, QtGui, QtWidgets

from core.models import RxEntry, TxMessageModel
from gui.console import ConsoleWidget
from gui.message_monitor import MessageMonitor
from gui.generator_panel import GeneratorPanel
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
    start_virtual_requested = QtCore.Signal(int, list, bool)
    stop_virtual_requested = QtCore.Signal()
    theme_toggle_requested = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jadoe CAN Studio")
        self.resize(1200, 800)

        self.monitor = MessageMonitor()
        self.signal_view = SignalView()
        self.tx_panel = TransmitPanel()
        self.generator_panel = GeneratorPanel()
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

        generator_dock = QtWidgets.QDockWidget("Interactive Generator", self)
        generator_dock.setWidget(self.generator_panel)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, generator_dock)

        self.generator_panel.start_requested.connect(self.start_virtual_requested.emit)
        self.generator_panel.stop_requested.connect(self.stop_virtual_requested.emit)

        console_dock = QtWidgets.QDockWidget("Console", self)
        console_dock.setWidget(self.console)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, console_dock)

        self._build_toolbar()
        self._build_statusbar()

    def _build_toolbar(self) -> None:
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        actions = {
            "Open DBC": ("ctrl+o", self.load_dbc_requested.emit),
            "Unload DBC": ("ctrl+shift+o", self.unload_dbc_requested.emit),
            "Connect": ("ctrl+c", self.connect_requested.emit),
            "Disconnect": ("ctrl+d", self.disconnect_requested.emit),
            "Start Logging": ("ctrl+l", self.start_logging_requested.emit),
            "Stop Logging": ("ctrl+shift+l", self.stop_logging_requested.emit),
            "Start Replay": ("ctrl+r", self.start_replay_requested.emit),
            "Stop Replay": ("ctrl+shift+r", self.stop_replay_requested.emit),
            "Toggle Theme": ("ctrl+t", self.theme_toggle_requested.emit),
        }
        for text, (shortcut, slot) in actions.items():
            action = QtGui.QAction(text, self)
            action.setShortcut(shortcut)
            action.triggered.connect(slot)
            toolbar.addAction(action)

        start_virtual = QtGui.QAction("Start Virtual", self)
        start_virtual.setShortcut("ctrl+shift+v")
        start_virtual.triggered.connect(self.generator_panel.start)
        toolbar.addAction(start_virtual)

        stop_virtual = QtGui.QAction("Stop Virtual", self)
        stop_virtual.setShortcut("ctrl+alt+v")
        stop_virtual.triggered.connect(self.generator_panel.stop_requested.emit)
        toolbar.addAction(stop_virtual)

    def _build_statusbar(self) -> None:
        self.status_messages = QtWidgets.QLabel("Disconnected")
        self.status_rx_count = QtWidgets.QLabel("Rx: 0")
        self.status_logging = QtWidgets.QLabel("Logging: stopped")
        self.status_virtual = QtWidgets.QLabel("Virtual: off")
        bar = self.statusBar()
        bar.addPermanentWidget(self.status_messages)
        bar.addPermanentWidget(self.status_rx_count)
        bar.addPermanentWidget(self.status_logging)
        bar.addPermanentWidget(self.status_virtual)

    def update_rx(self, entries: Dict[str, RxEntry]) -> None:
        self.monitor.update_entries(list(entries.values()))
        self.status_rx_count.setText(f"Rx: {len(entries)}")

    def update_signals(self, signals: Dict[str, Dict[str, str]]) -> None:
        self.signal_view.update_signals(signals)

    def set_tx_models(self, models: Dict[str, TxMessageModel]) -> None:
        self.tx_panel.set_messages(models)
        self.tx_panel.connect_signals()
        self.generator_panel.set_messages(list(models.keys()))

    def log_message(self, text: str) -> None:
        self.console.log(text)

    def set_connection_status(self, connected: bool) -> None:
        self.status_messages.setText("Connected" if connected else "Disconnected")

    def set_logging_status(self, active: bool, path: Optional[Path] = None) -> None:
        label = "Logging: active" if active else "Logging: stopped"
        if active and path:
            label += f" ({path.name})"
        self.status_logging.setText(label)

    def set_virtual_status(self, active: bool) -> None:
        self.status_virtual.setText("Virtual: on" if active else "Virtual: off")

    def stop_generator_ui(self) -> None:
        self.generator_panel.stop()

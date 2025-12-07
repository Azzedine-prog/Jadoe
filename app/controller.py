"""Application controller bridging UI and core logic."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Optional

from PySide6 import QtCore

from core.config import BusConfig, WorkspaceSettings
from core.dbc_manager import DbcManager, DbcLoadError
from core.models import RxBuffer, RxEntry, TxMessageModel
from gui.main_window import MainWindow
from canio.can_bus import CanBusController, ReceivedMessage
from canio.logger import SessionLogger
from canio.virtual import VirtualCanGenerator


class ApplicationController(QtCore.QObject):
    def __init__(self, window: MainWindow, settings: WorkspaceSettings, theme_manager) -> None:
        super().__init__()
        self.window = window
        self.settings = settings
        self.theme_manager = theme_manager
        self.dbc_manager = DbcManager()
        self.rx_buffer = RxBuffer()
        self.logger: Optional[SessionLogger] = None
        self.bus_controller = CanBusController(settings.bus)
        self.bus_controller.set_callback(self.on_message_received)
        self.virtual_generator = VirtualCanGenerator(self.dbc_manager, self.on_message_received)
        self.cyclic_timers: Dict[str, QtCore.QTimer] = {}

        self._connect_ui()

        if settings.last_dbc:
            self._load_dbc(Path(settings.last_dbc))

    # UI wiring
    def _connect_ui(self) -> None:
        self.window.load_dbc_requested.connect(self._choose_and_load_dbc)
        self.window.unload_dbc_requested.connect(self._unload_dbc)
        self.window.connect_requested.connect(self._connect_bus)
        self.window.disconnect_requested.connect(self._disconnect_bus)
        self.window.start_logging_requested.connect(self._start_logging)
        self.window.stop_logging_requested.connect(self._stop_logging)
        self.window.start_virtual_requested.connect(self._start_virtual)
        self.window.stop_virtual_requested.connect(self._stop_virtual)
        self.window.theme_toggle_requested.connect(self._toggle_theme)
        self.window.tx_panel.send_once.connect(self._send_once)
        self.window.tx_panel.toggle_cyclic.connect(self._handle_cyclic)
        self.window.monitor.selection_changed.connect(self._update_signal_view)

    # DBC handling
    def _choose_and_load_dbc(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.window, "Open DBC", str(Path.cwd()), "DBC Files (*.dbc)"
        )
        if path:
            self._load_dbc(Path(path))

    def _load_dbc(self, path: Path) -> None:
        try:
            loaded = self.dbc_manager.load(path)
        except DbcLoadError as exc:
            QtWidgets.QMessageBox.critical(self.window, "DBC Error", str(exc))
            self.window.log_message(f"Failed to load DBC: {exc}")
            return
        self.window.log_message(f"Loaded DBC: {path}")
        self.settings.last_dbc = str(path)
        self.settings.save()
        models = {msg.name: TxMessageModel.from_message(msg) for msg in loaded.messages}
        self.window.set_tx_models(models)

    def _unload_dbc(self) -> None:
        self.dbc_manager.unload()
        self.window.log_message("DBC unloaded")
        self.window.set_tx_models({})
        self._stop_virtual()

    # Bus handling
    def _connect_bus(self) -> None:
        try:
            self.bus_controller.start()
        except Exception as exc:  # noqa: BLE001 - show to user
            QtWidgets.QMessageBox.critical(self.window, "Bus Error", str(exc))
            return
        self.window.set_connection_status(True)
        self.window.log_message("CAN bus connected")

    def _disconnect_bus(self) -> None:
        self.bus_controller.stop()
        self.window.set_connection_status(False)
        self.window.log_message("CAN bus disconnected")

    def on_message_received(self, message: ReceivedMessage) -> None:
        loaded = self.dbc_manager.loaded
        decoded = loaded.decode(message.arbitration_id, message.data) if loaded else {}
        name = loaded.message_by_id(message.arbitration_id).name if loaded and loaded.message_by_id(message.arbitration_id) else None
        data_hex = " ".join(f"{b:02X}" for b in message.data)
        entry = RxEntry(
            timestamp=message.timestamp,
            arbitration_id=message.arbitration_id,
            dlc=len(message.data),
            data_hex=data_hex,
            decoded=decoded,
            message_name=name,
        )
        self.rx_buffer.append(entry)
        QtCore.QMetaObject.invokeMethod(
            self.window, lambda: self.window.monitor.update_entries(self.rx_buffer.entries), QtCore.Qt.QueuedConnection
        )
        if self.logger:
            self.logger.log(message)

    # Virtual generator
    def _start_virtual(self, period_ms: int, messages: list[str], randomize: bool) -> None:
        if not self.dbc_manager.loaded:
            QtWidgets.QMessageBox.warning(self.window, "DBC", "Load a DBC before starting virtual mode")
            self.window.stop_generator_ui()
            return
        self.virtual_generator.start(period_ms, messages, randomize)
        self.window.set_virtual_status(True)
        self.window.log_message(
            f"Virtual generator running every {period_ms} ms for {len(messages) if messages else 'all'} messages"
        )

    def _stop_virtual(self) -> None:
        self.virtual_generator.stop()
        self.window.set_virtual_status(False)
        self.window.stop_generator_ui()
        self.window.log_message("Virtual generator stopped")

    # Logging
    def _start_logging(self) -> None:
        logs_dir = Path.cwd() / "logs"
        logs_dir.mkdir(exist_ok=True)
        path = logs_dir / f"session-{int(time.time())}.csv"
        self.logger = SessionLogger(path)
        self.window.set_logging_status(True, path)
        self.window.log_message(f"Logging to {path}")

    def _stop_logging(self) -> None:
        if self.logger:
            self.logger.close()
        self.logger = None
        self.window.set_logging_status(False)
        self.window.log_message("Logging stopped")

    # Transmit
    def _send_once(self, message_name: str, signals: Dict[str, float]) -> None:
        loaded = self.dbc_manager.loaded
        if not loaded:
            QtWidgets.QMessageBox.warning(self.window, "DBC", "Load a DBC first")
            return
        data = loaded.encode(message_name, signals)
        message = loaded.database.get_message_by_name(message_name)
        assert message
        self.bus_controller.send(message.frame_id, data, message.is_extended_frame)
        self.window.log_message(f"Sent {message_name} ({message.frame_id:#x})")

    def _handle_cyclic(self, message_name: str, signals: Dict[str, float], period_ms: int, active: bool) -> None:
        if active:
            timer = QtCore.QTimer(self)
            timer.setInterval(period_ms)
            timer.timeout.connect(lambda: self._send_once(message_name, signals))
            timer.start()
            self.cyclic_timers[message_name] = timer
        else:
            timer = self.cyclic_timers.pop(message_name, None)
            if timer:
                timer.stop()

    def _update_signal_view(self, index: int) -> None:
        entry = self.window.monitor.current_entry()
        if not entry:
            return
        loaded = self.dbc_manager.loaded
        if not loaded or not entry.message_name:
            return
        message = loaded.database.get_message_by_name(entry.message_name)
        if not message:
            return
        signals = {}
        for signal in message.signals:
            raw = entry.decoded.get(signal.name)
            signals[signal.name] = {
                "phys": raw,
                "raw": raw,
                "unit": signal.unit or "",
                "range": f"{signal.minimum}..{signal.maximum}",
            }
        self.window.update_signals(signals)

    # Theme
    def _toggle_theme(self) -> None:
        self.theme_manager.toggle(QtWidgets.QApplication.instance())  # type: ignore[arg-type]


# Late import to avoid circular Qt reference
from PySide6 import QtWidgets  # noqa: E402  

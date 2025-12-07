"""Transmit panel for crafting CAN messages."""
from __future__ import annotations

from typing import Callable, Dict, Optional

from PySide6 import QtCore, QtWidgets

from core.models import TxMessageModel


class TransmitPanel(QtWidgets.QWidget):
    send_once = QtCore.Signal(str, dict)
    toggle_cyclic = QtCore.Signal(str, dict, int, bool)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.message_combo = QtWidgets.QComboBox()
        self.period_spin = QtWidgets.QSpinBox()
        self.period_spin.setRange(10, 5000)
        self.period_spin.setValue(1000)
        self.form_layout = QtWidgets.QFormLayout()
        self.signal_form = QtWidgets.QWidget()
        self.signal_form.setLayout(self.form_layout)
        self.send_button = QtWidgets.QPushButton("Send once")
        self.cyclic_button = QtWidgets.QPushButton("Start cyclic")

        top = QtWidgets.QHBoxLayout()
        top.addWidget(QtWidgets.QLabel("Message"))
        top.addWidget(self.message_combo)
        top.addWidget(QtWidgets.QLabel("Period (ms)"))
        top.addWidget(self.period_spin)
        top.addStretch()
        top.addWidget(self.send_button)
        top.addWidget(self.cyclic_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.signal_form)

        self.send_button.clicked.connect(self._emit_send)
        self.cyclic_button.clicked.connect(self._toggle_cyclic)

        self._models: Dict[str, TxMessageModel] = {}
        self._cyclic_running = False

    def set_messages(self, models: Dict[str, TxMessageModel]) -> None:
        self._models = models
        self.message_combo.clear()
        for name in models:
            self.message_combo.addItem(name)
        self._rebuild_signals()

    def _rebuild_signals(self) -> None:
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)
        name = self.message_combo.currentText()
        if not name:
            return
        model = self._models[name]
        for signal_name, tx_signal in model.signals.items():
            spin = QtWidgets.QDoubleSpinBox()
            spin.setRange(-1e9, 1e9)
            spin.setValue(tx_signal.value)
            spin.valueChanged.connect(lambda val, sn=signal_name: self._on_signal_change(sn, val))
            self.form_layout.addRow(signal_name, spin)

    def _on_signal_change(self, signal_name: str, value: float) -> None:
        name = self.message_combo.currentText()
        if name and name in self._models:
            self._models[name].signals[signal_name].value = value

    def _emit_send(self) -> None:
        name = self.message_combo.currentText()
        if not name:
            return
        model = self._models[name]
        self.send_once.emit(name, {k: v.value for k, v in model.signals.items()})

    def _toggle_cyclic(self) -> None:
        name = self.message_combo.currentText()
        if not name:
            return
        model = self._models[name]
        active = not model.active
        model.active = active
        period = self.period_spin.value()
        self.cyclic_button.setText("Stop cyclic" if active else "Start cyclic")
        self.toggle_cyclic.emit(name, {k: v.value for k, v in model.signals.items()}, period, active)

    def connect_signals(self) -> None:
        self.message_combo.currentTextChanged.connect(lambda _: self._rebuild_signals())

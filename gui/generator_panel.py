"""Interactive generator panel for virtual CAN traffic."""
from __future__ import annotations

from typing import List, Optional

from PySide6 import QtCore, QtWidgets


class GeneratorPanel(QtWidgets.QWidget):
    """Provides controls for a virtual message generator similar to CANoe IG."""

    start_requested = QtCore.Signal(int, list, bool)
    stop_requested = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.period_spin = QtWidgets.QSpinBox()
        self.period_spin.setRange(20, 5000)
        self.period_spin.setValue(200)
        self.period_spin.setSuffix(" ms")

        self.randomize_box = QtWidgets.QCheckBox("Randomize signals each cycle")
        self.randomize_box.setChecked(True)

        self.message_list = QtWidgets.QListWidget()
        self.message_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.message_list.setUniformItemSizes(True)

        self.toggle_button = QtWidgets.QPushButton("Start virtual")
        self.toggle_button.clicked.connect(self._toggle)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Select messages to synthesize (empty = all):"))
        layout.addWidget(self.message_list)

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(QtWidgets.QLabel("Period:"))
        controls.addWidget(self.period_spin)
        controls.addWidget(self.randomize_box)
        controls.addStretch()
        controls.addWidget(self.toggle_button)
        layout.addLayout(controls)

        self._running = False

    def set_messages(self, messages: List[str]) -> None:
        """Populate the message list with available DBC messages."""
        self.message_list.clear()
        for name in messages:
            item = QtWidgets.QListWidgetItem(name)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.message_list.addItem(item)

    def _selected_messages(self) -> List[str]:
        selected: List[str] = []
        for i in range(self.message_list.count()):
            item = self.message_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                selected.append(item.text())
        return selected

    def _toggle(self) -> None:
        if not self._running:
            self.start()
        else:
            self.stop_requested.emit()
            self.toggle_button.setText("Start virtual")
            self._running = False

    def stop(self) -> None:
        """Reset UI state when generator is stopped externally."""
        if self._running:
            self._running = False
            self.toggle_button.setText("Start virtual")

    def start(self) -> None:
        """Start the generator using current settings if not already active."""
        if self._running:
            return
        period = self.period_spin.value()
        selected = self._selected_messages()
        self.start_requested.emit(period, selected, self.randomize_box.isChecked())
        self.toggle_button.setText("Stop virtual")
        self._running = True

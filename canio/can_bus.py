"""CAN bus backend abstraction built on python-can."""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

import can

from core.config import BusConfig


@dataclass
class ReceivedMessage:
    timestamp: float
    arbitration_id: int
    data: bytes
    is_extended_id: bool


class CanBusController:
    """High-level controller for python-can Bus with callbacks."""

    def __init__(self, config: BusConfig) -> None:
        self.config = config
        self._bus: Optional[can.Bus] = None
        self._listener_thread: Optional[threading.Thread] = None
        self._running = False
        self._callback: Optional[Callable[[ReceivedMessage], None]] = None

    @property
    def is_running(self) -> bool:
        return self._running

    def set_callback(self, callback: Callable[[ReceivedMessage], None]) -> None:
        self._callback = callback

    def start(self) -> None:
        if self._running:
            return
        self._bus = can.Bus(**self.config.to_kwargs())
        self._running = True
        self._listener_thread = threading.Thread(target=self._listen, daemon=True)
        self._listener_thread.start()

    def stop(self) -> None:
        self._running = False
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=1)
        if self._bus:
            self._bus.shutdown()
            self._bus = None

    def send(self, arbitration_id: int, data: bytes, is_extended_id: bool = False) -> None:
        if not self._bus:
            raise RuntimeError("CAN bus not started")
        msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=is_extended_id)
        self._bus.send(msg)

    def _listen(self) -> None:
        assert self._bus
        while self._running:
            msg = self._bus.recv(timeout=0.1)
            if msg is None:
                continue
            if self._callback:
                event = ReceivedMessage(
                    timestamp=time.time(),
                    arbitration_id=msg.arbitration_id,
                    data=bytes(msg.data),
                    is_extended_id=msg.is_extended_id,
                )
                self._callback(event)

"""Virtual CAN generator for offline testing."""
from __future__ import annotations

import random
import threading
import time
from typing import Dict, Iterable, Optional, Set

from canio.can_bus import ReceivedMessage
from core.dbc_manager import DbcManager


class VirtualCanGenerator:
    """Synthesizes CAN frames from a loaded DBC for UI testing."""

    def __init__(self, dbc_manager: DbcManager, callback) -> None:
        self.dbc_manager = dbc_manager
        self._callback = callback
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._period = 0.2
        self._message_filter: Optional[Set[str]] = None
        self._incrementers: Dict[str, int] = {}
        self._randomize = True

    def start(self, period_ms: int, messages: Iterable[str] | None = None, randomize: bool = True) -> None:
        if self._running:
            self.stop()
        self._period = max(10, period_ms) / 1000.0
        self._message_filter = set(messages) if messages else None
        self._randomize = randomize
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        self._thread = None

    def _run(self) -> None:
        while self._running:
            loaded = self.dbc_manager.loaded
            if not loaded:
                time.sleep(self._period)
                continue
            for message in loaded.messages:
                if self._message_filter and message.name not in self._message_filter:
                    continue
                data = self._build_payload(message)
                event = ReceivedMessage(
                    timestamp=time.time(),
                    arbitration_id=message.frame_id,
                    data=data,
                    is_extended_id=message.is_extended_frame,
                )
                self._callback(event)
            time.sleep(self._period)

    def _build_payload(self, message) -> bytes:
        payload: Dict[str, float] = {}
        for signal in message.signals:
            if self._randomize:
                minimum = signal.minimum if signal.minimum is not None else 0
                maximum = signal.maximum if signal.maximum is not None else minimum + 100
                payload[signal.name] = random.uniform(minimum, maximum)
            else:
                step = self._incrementers.get(signal.name, 0)
                payload[signal.name] = step
                self._incrementers[signal.name] = (step + 1) % 1000
        return message.encode(payload)

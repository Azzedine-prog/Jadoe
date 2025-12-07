"""Logging and replay utilities."""
from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Iterable, Iterator, List, Optional

from canio.can_bus import ReceivedMessage


class SessionLogger:
    """Logs CAN traffic to CSV with decoded metadata."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._file = path.open("w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow(["timestamp", "id", "dlc", "data"])

    def log(self, message: ReceivedMessage) -> None:
        data_hex = " ".join(f"{b:02X}" for b in message.data)
        self._writer.writerow([
            f"{message.timestamp:.6f}",
            hex(message.arbitration_id),
            len(message.data),
            data_hex,
        ])
        self._file.flush()

    def close(self) -> None:
        self._file.close()


class ReplayEvent:
    def __init__(self, timestamp: float, arbitration_id: int, data: bytes) -> None:
        self.timestamp = timestamp
        self.arbitration_id = arbitration_id
        self.data = data


class LogReplay:
    """Replay recorded log files with pacing control."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._rows: List[ReplayEvent] = []
        self._load()

    def _load(self) -> None:
        with self.path.open() as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                ts = float(row["timestamp"])
                arb_id = int(row["id"], 16)
                data = bytes(int(b, 16) for b in row["data"].split())
                self._rows.append(ReplayEvent(ts, arb_id, data))

    def iter_events(self, speed: float = 1.0, loop: bool = False) -> Iterator[ReceivedMessage]:
        while True:
            base: Optional[float] = None
            for event in self._rows:
                if base is None:
                    base = event.timestamp
                delay = (event.timestamp - base) / speed
                if delay > 0:
                    time.sleep(delay)
                yield ReceivedMessage(time.time(), event.arbitration_id, event.data, False)
            if not loop:
                break

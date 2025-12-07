"""Data models for received and transmit messages."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from cantools.database.can import Message


@dataclass
class RxEntry:
    """Represents a message in the receive buffer."""

    timestamp: float
    arbitration_id: int
    dlc: int
    data_hex: str
    decoded: Dict[str, float] = field(default_factory=dict)
    message_name: Optional[str] = None


class RxBuffer:
    """Bounded buffer for received frames."""

    def __init__(self, limit: int = 2000) -> None:
        self.limit = limit
        self._entries: List[RxEntry] = []

    def append(self, entry: RxEntry) -> None:
        self._entries.insert(0, entry)
        if len(self._entries) > self.limit:
            self._entries.pop()

    @property
    def entries(self) -> List[RxEntry]:
        return list(self._entries)


@dataclass
class TxSignalValue:
    name: str
    value: float


@dataclass
class TxMessageModel:
    message: Message
    signals: Dict[str, TxSignalValue]
    period_ms: Optional[int] = None
    active: bool = False

    @classmethod
    def from_message(cls, message: Message) -> "TxMessageModel":
        return cls(
            message=message,
            signals={sig.name: TxSignalValue(sig.name, 0) for sig in message.signals},
        )

    def payload(self) -> bytes:
        payload = {name: sig.value for name, sig in self.signals.items()}
        return self.message.encode(payload)

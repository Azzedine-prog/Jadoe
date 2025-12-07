"""DBC management and decoding utilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import cantools
from cantools.database import Database
from cantools.database.can import Message, Signal


class DbcLoadError(Exception):
    """Raised when DBC parsing fails."""


@dataclass
class LoadedDbc:
    """Represents a loaded DBC with convenient lookups."""

    path: Path
    database: Database

    @property
    def messages(self) -> List[Message]:
        return list(self.database.messages)

    def message_by_id(self, can_id: int) -> Optional[Message]:
        return self.database.get_message_by_frame_id(can_id)

    def decode(self, can_id: int, data: bytes) -> Dict[str, float]:
        message = self.message_by_id(can_id)
        if not message:
            return {}
        return message.decode(data)

    def encode(self, message_name: str, signals: Dict[str, float]) -> bytes:
        message = self.database.get_message_by_name(message_name)
        if not message:
            raise KeyError(f"Message {message_name} not found")
        return message.encode(signals)


class DbcManager:
    """Wrapper around cantools to manage DBC lifecycle."""

    def __init__(self) -> None:
        self._loaded: Optional[LoadedDbc] = None

    @property
    def loaded(self) -> Optional[LoadedDbc]:
        return self._loaded

    def load(self, path: Path) -> LoadedDbc:
        try:
            db = cantools.database.load_file(path)
        except Exception as exc:  # noqa: BLE001 - propagate as typed exception
            raise DbcLoadError(str(exc)) from exc
        self._loaded = LoadedDbc(path=path, database=db)
        return self._loaded

    def unload(self) -> None:
        self._loaded = None

    def validate_bitrate(self, bitrate: int) -> bool:
        # Placeholder for more advanced validation logic
        return bitrate > 0

    def describe(self) -> Dict[str, List[Dict[str, str]]]:
        if not self._loaded:
            return {}
        result: List[Dict[str, str]] = []
        for msg in self._loaded.messages:
            result.append(
                {
                    "name": msg.name,
                    "id": hex(msg.frame_id),
                    "dlc": str(msg.length),
                    "signals": ", ".join(sig.name for sig in msg.signals),
                }
            )
        return {"messages": result}

    def signals_for_message(self, message: Message) -> List[Signal]:
        return list(message.signals)

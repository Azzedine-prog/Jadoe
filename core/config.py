"""Configuration management for CAN application."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


CONFIG_DIR = Path.home() / ".jadoe"
CONFIG_FILE = CONFIG_DIR / "workspace.json"


@dataclass
class BusConfig:
    """Configuration for a CAN bus backend."""

    channel: str = "vcan0"
    interface: str = "virtual"
    bitrate: int = 500000
    fd: bool = False

    def to_kwargs(self) -> Dict[str, Any]:
        """Translate configuration to python-can Bus parameters."""
        kwargs: Dict[str, Any] = {
            "channel": self.channel,
            "bustype": self.interface,
            "bitrate": self.bitrate,
        }
        if self.fd:
            kwargs["fd"] = True
        return kwargs


@dataclass
class WorkspaceSettings:
    """Persisted workspace settings."""

    last_dbc: Optional[str] = None
    bus: BusConfig = field(default_factory=BusConfig)
    layout_state: Optional[str] = None
    tx_workspace: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path = CONFIG_FILE) -> "WorkspaceSettings":
        if not path.exists():
            return cls()
        data = json.loads(path.read_text())
        bus_data = data.get("bus", {})
        return cls(
            last_dbc=data.get("last_dbc"),
            bus=BusConfig(**bus_data),
            layout_state=data.get("layout_state"),
            tx_workspace=data.get("tx_workspace", {}),
        )

    def save(self, path: Path = CONFIG_FILE) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        path.write_text(json.dumps(payload, indent=2))

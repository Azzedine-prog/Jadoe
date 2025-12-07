from pathlib import Path

from core.config import WorkspaceSettings, BusConfig


def test_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "workspace.json"
    settings = WorkspaceSettings(last_dbc="demo.dbc", bus=BusConfig(channel="vcan1", interface="socketcan"))
    settings.save(path)

    loaded = WorkspaceSettings.load(path)
    assert loaded.last_dbc == "demo.dbc"
    assert loaded.bus.channel == "vcan1"
    assert loaded.bus.interface == "socketcan"

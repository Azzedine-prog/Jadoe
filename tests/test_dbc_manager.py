from pathlib import Path

import pytest

from core.dbc_manager import DbcManager, DbcLoadError


def test_load_and_decode() -> None:
    manager = DbcManager()
    loaded = manager.load(Path("data/sample.dbc"))
    message = loaded.database.get_message_by_name("ExampleMessage")
    encoded = message.encode({"Speed": 100.0, "Rpm": 1500})
    decoded = loaded.decode(message.frame_id, encoded)
    assert decoded["Speed"] == pytest.approx(100.0)
    assert decoded["Rpm"] == pytest.approx(1500)


def test_invalid_file(tmp_path: Path) -> None:
    bad = tmp_path / "bad.dbc"
    bad.write_text("BOGUS")
    manager = DbcManager()
    with pytest.raises(DbcLoadError):
        manager.load(bad)

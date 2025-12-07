# Jadoe CAN Studio

Jadoe CAN Studio is a lightweight, production-style Python desktop application for inspecting and transmitting CAN traffic using a DBC-centric workflow. It mirrors familiar workflows from tools like Vector CANoe but is built entirely with open tooling.

## Features
- Load/unload DBC files using `cantools`, browse messages and signals.
- Configure CAN backends through `python-can` (virtual, SocketCAN, Vector, etc.).
- Live RX monitor with decoded signal view and selection-driven signal details.
- Transmit panel with single-shot and cyclic sending using DBC-defined signals.
- Session logging to CSV and basic replay support (logic provided for integration).
- Dark/light themes via a central `ThemeManager` for modern UI styling.
- Workspace persistence for last DBC, bus configuration, and layout state.

## Project Structure
- `app/` – entry point and application wiring.
- `core/` – business logic for configuration, DBC parsing, and data models.
- `gui/` – PySide6 user interface components (no CAN logic here).
- `canio/` – CAN backend abstraction and logging/replay utilities.
- `tests/` – unit tests for configuration and DBC parsing.
- `data/` – sample DBC file for demo/testing.

## Getting Started
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install PySide6 python-can cantools pytest
   ```
2. Launch the application:
   ```bash
   python -m app.main
   ```
3. Use the toolbar to load a DBC, connect to a CAN interface, and start monitoring or transmitting.

## Testing
Run the unit tests with pytest:
```bash
pytest
```

## Notes
- The default CAN configuration targets a virtual bus (`vcan0`) at 500 kbit/s. Adjust via the UI or by editing `core/config.py` defaults.
- Logging writes CSV files to a local `logs/` directory. Replay logic is available in `canio/logger.py` and can be wired to a virtual bus for offline analysis.

# Stampede Swift Configuration UI

Native macOS SwiftUI replacement for `config_gui.py`. It keeps the existing Python monitoring pipeline and launches
`main.py --config-file <temp.json>` with the selected settings.

## Run

From the repository root:

```bash
swift run --package-path swift-ui StampedeConfigSwift
```

The app prefers `STAMPEDE_PYTHON`, then an active virtualenv, then repo-local `.venv`, `venv`, `env`, or `ENV`
interpreters that can import `cv2`.

Recommended first-time setup:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
swift run --package-path swift-ui StampedeConfigSwift
```

If the app cannot locate the repository, set `STAMPEDE_APP_DIR` to the Stampede-Management directory. If the monitor
needs a specific Python interpreter or virtual environment, set `STAMPEDE_PYTHON` to that Python executable before
launching.

# Contributing

Contributions are welcome! Here's how to get started.

## Development setup

1. Clone the repository
2. Install Python 3.12+
3. Install dependencies: `pip install -r requirements.txt`
4. Run with: `py run.py`

## Code structure

- `src/zscore_toolbox/main.py` — entry point, tray icon, measurement orchestration
- `src/zscore_toolbox/ui.py` — Tkinter overlay, step panel, result/error popups
- `src/zscore_toolbox/capture.py` — screenshot capture
- `src/zscore_toolbox/calculator.py` — Z-score math

## Guidelines

- Keep the UI simple and fast — this is a quick-measure tool
- All user-facing text must be in English
- Add type hints to all public functions
- Use named constants for magic values (colors, delays, sizes)
- Test that `run.py` still works after changes
- Test that the PyInstaller build still produces a working EXE
- Run `bandit -r src/` locally before submitting a PR to catch security issues

## Submitting changes

1. Fork the repository
2. Create a feature branch
3. Make your changes and test locally
4. Submit a pull request with a clear description

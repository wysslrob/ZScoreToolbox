# Z-Score Toolbox

A Windows System Tray tool for measuring Z-scores directly on screen.
Click four reference points on any chart or image and the app instantly
calculates and displays the Z-score.

## How it works

1. The app sits in the system tray.
2. Click the tray icon (or choose **Z-Score messen**) to take a screenshot.
3. Click four points on the screenshot in order:
   - **Mean** – the mean / zero line
   - **+1 SD** – one standard deviation above the mean
   - **-1 SD** – one standard deviation below the mean
   - **Messpunkt** – the value you want to measure
4. The Z-score is displayed in a popup.

Press **ESC** at any time to cancel the measurement.

## Installation

```bash
python -m pip install -r requirements.txt
```

Requires **Python 3.10+** and **Windows** (pystray uses the Windows tray API).

## Usage

```bash
python -m zscore_toolbox.main
```

Or, after installing as a package:

```bash
zscore-toolbox
```

## Project structure

```
ZScoreToolbox/
├── src/
│   └── zscore_toolbox/
│       ├── __init__.py       # package metadata
│       ├── main.py           # entry point, tray icon
│       ├── capture.py        # screenshot logic (mss)
│       ├── ui.py             # ClickWindow, popups, Tkinter thread
│       └── calculator.py     # Z-score calculation
├── assets/                   # icon files (icon.ico for the EXE)
├── build_tools/
│   └── build.bat             # PyInstaller build script
├── requirements.txt
└── README.md
```

## Building a standalone EXE

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Place your icon file at `assets\icon.ico`.
3. Run the build script from the repository root:
   ```bat
   build_tools\build.bat
   ```
4. The finished `ZScoreToolbox.exe` will be in the `dist\` folder.

> **Note:** `build/`, `dist/`, and `*.spec` are excluded by `.gitignore`.

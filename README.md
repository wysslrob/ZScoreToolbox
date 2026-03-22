# Z-Score Toolbox

A system tray tool for measuring Z-scores directly on screen.

## How it works

1. Click the tray icon and select **Measure Z-Score**.
2. A screenshot appears with a dark overlay — click four points in order:
   - **Mean** — the zero / mean line (blue)
   - **+1 SD** — one standard deviation above (green)
   - **-1 SD** — one standard deviation below (red)
   - **Point** — the value you want to measure (yellow)
3. A step-by-step panel on the left guides you through each click.
4. The Z-score is shown in a popup with a visual gauge, copy button, and option to measure again.

Press **ESC** at any time to cancel.

---

## Setup

**1. Install Python 3.12** (Windows, via winget):

```bat
winget install Python.Python.3.12
```

**2. Install dependencies:**

```bat
pip install -r requirements.txt
```

**3. Run:**

```bat
py run.py
```

---

## Build standalone EXE

**1. Install PyInstaller:**

```bat
pip install pyinstaller
```

**2. Place your icon at `assets\icon.ico`, then run:**

```bat
build_tools\build.bat
```

The finished `ZScoreToolbox.exe` will be in the `dist\` folder.

---

## Project structure

```
ZScoreToolbox/
├── src/zscore_toolbox/
│   ├── main.py          # entry point, tray icon, measurement workflow
│   ├── capture.py       # screenshot capture via mss
│   ├── ui.py            # click overlay, step panel, result/error popups
│   └── calculator.py    # Z-score calculation
├── assets/              # icon.ico (for PyInstaller builds)
├── build_tools/
│   └── build.bat        # PyInstaller build script
├── run.py               # development entry point
└── requirements.txt
```

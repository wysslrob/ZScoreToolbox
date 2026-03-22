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

**2. Generate the application icon:**

```bat
py build_tools/generate_icon.py
```

This creates `assets\icon.ico` with all required sizes (16–256 px).
The build script runs this automatically, but you can also run it
manually to preview the icon beforehand.

**3. Build the EXE:**

```bat
build_tools\build.bat
```

The build script generates the icon first, then runs PyInstaller with
`--icon=assets/icon.ico`. The finished `ZScoreToolbox.exe` will be in
the `dist\` folder.

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
│   ├── build.bat        # PyInstaller build script
│   └── generate_icon.py # generates assets/icon.ico via Pillow
├── run.py               # development entry point
└── requirements.txt
```

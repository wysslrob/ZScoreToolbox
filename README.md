# Z-Score Toolbox

Windows system tray tool to measure Z-scores directly on screen.

## How it works

1. Click the tray icon and select **Z-Score messen**.
2. A screenshot appears — click four points in order:
   - **Mean** – the zero / mean line
   - **+1 SD** – one standard deviation above
   - **-1 SD** – one standard deviation below
   - **Messpunkt** – the value to measure
3. The Z-score is shown in a popup.

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
cd src
py -m zscore_toolbox.main
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
│   ├── main.py          # entry point, tray icon
│   ├── capture.py       # screenshot logic
│   ├── ui.py            # click window & popups
│   └── calculator.py    # Z-score calculation
├── assets/              # icon.ico
├── build_tools/
│   └── build.bat        # PyInstaller build script
└── requirements.txt
```

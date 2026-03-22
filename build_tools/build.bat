@echo off
REM Build ZScoreToolbox into a single EXE with PyInstaller.
REM Run this script from the repository root.

echo Generating application icon...
py build_tools/generate_icon.py
if errorlevel 1 (
    echo WARNING: Icon generation failed — building without custom icon.
    pyinstaller --onefile --windowed --name "ZScoreToolbox" ^
      --paths src ^
      run.py
) else (
    pyinstaller --onefile --windowed --name "ZScoreToolbox" ^
      --paths src ^
      --icon=assets/icon.ico ^
      run.py
)

echo.
echo Build complete. EXE is in the dist\ folder.
pause

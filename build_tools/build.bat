@echo off
REM Build ZScoreToolbox into a single EXE with PyInstaller.
REM Run this script from the repository root.

pyinstaller --onefile --windowed --name "ZScoreToolbox" ^
  --paths src ^
  run.py

echo.
echo Build complete. EXE is in the dist\ folder.
pause

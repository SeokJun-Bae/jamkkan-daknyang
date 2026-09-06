@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Creating Python virtual environment...
    py -m venv .venv || goto :error
)

echo [2/4] Installing build dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements-build.txt || goto :error

echo [3/4] Running tests...
".venv\Scripts\python.exe" -m pytest -q || goto :error

echo [4/4] Building JamkkanDaknyang.exe...
".venv\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "JamkkanDaknyang" ^
    main.py || goto :error

echo.
echo Build complete: dist\JamkkanDaknyang.exe
start "" "%~dp0dist"
exit /b 0

:error
echo.
echo Build failed. Review the error output above.
pause
exit /b 1

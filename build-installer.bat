@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

call build.bat || goto :error

set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if not exist "%ISCC%" (
    echo Inno Setup is required to build the installer.
    echo Installing Inno Setup with WinGet...
    winget install --id JRSoftware.InnoSetup -e --source winget || goto :error
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    if not exist "!ISCC!" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)

for /f "delims=" %%V in ('.venv\Scripts\python.exe -c "from dakknyang import __version__; print(__version__)"') do set "APP_VERSION=%%V"
if not defined APP_VERSION goto :error

echo Building installer for version %APP_VERSION%...
"%ISCC%" "/DMyAppVersion=%APP_VERSION%" "installer.iss" || goto :error

echo.
echo Installer complete: dist\JamkkanDaknyang-Setup.exe
start "" "%~dp0dist"
exit /b 0

:error
echo.
echo Installer build failed. Review the error output above.
pause
exit /b 1

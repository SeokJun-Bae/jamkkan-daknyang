@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

where git >nul 2>nul || (
    echo Git is not installed or is missing from PATH.
    pause
    exit /b 1
)

for /f "delims=" %%V in ('py -c "from dakknyang import __version__; print(__version__)"') do set "APP_VERSION=%%V"
if not defined APP_VERSION (
    echo Could not read the application version.
    pause
    exit /b 1
)

for /f "delims=" %%S in ('git status --porcelain') do set "CHANGES=1"
if defined CHANGES (
    echo Uncommitted changes were found.
    echo Run git add and git commit before releasing.
    git status --short
    pause
    exit /b 1
)

git rev-parse "v%APP_VERSION%" >nul 2>nul && (
    echo Tag v%APP_VERSION% already exists.
    echo Increase __version__ in dakknyang\__init__.py for a new release.
    pause
    exit /b 1
)

echo Pushing the current commit...
git push origin HEAD || goto :error

echo Creating release tag v%APP_VERSION%...
git tag -a "v%APP_VERSION%" -m "Jamkkan Daknyang v%APP_VERSION%"
git push origin "v%APP_VERSION%" || goto :error

echo.
echo GitHub Actions is building the Windows executable.
echo Check the repository Actions or Releases page for progress.
pause
exit /b 0

:error
echo Release request failed. Check the Git remote and login status.
pause
exit /b 1

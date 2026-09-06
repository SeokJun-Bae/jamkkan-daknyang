@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Python 가상환경을 만듭니다.
    py -m venv .venv || goto :error
)

echo [2/4] 빌드 도구를 설치합니다.
".venv\Scripts\python.exe" -m pip install -r requirements-build.txt || goto :error

echo [3/4] 테스트를 실행합니다.
".venv\Scripts\python.exe" -m pytest -q || goto :error

echo [4/4] 잠깐닦냥.exe를 만듭니다.
".venv\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "잠깐닦냥" ^
    main.py || goto :error

echo.
echo 빌드 완료: dist\잠깐닦냥.exe
start "" "%~dp0dist"
exit /b 0

:error
echo.
echo 빌드에 실패했습니다. 위 오류 내용을 확인해 주세요.
pause
exit /b 1


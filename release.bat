@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

where git >nul 2>nul || (
    echo Git이 설치되어 있지 않거나 PATH에 등록되지 않았습니다.
    pause
    exit /b 1
)

for /f "delims=" %%V in ('py -c "from dakknyang import __version__; print(__version__)"') do set "APP_VERSION=%%V"
if not defined APP_VERSION (
    echo 버전 정보를 읽지 못했습니다.
    pause
    exit /b 1
)

for /f "delims=" %%S in ('git status --porcelain') do set "CHANGES=1"
if defined CHANGES (
    echo 커밋되지 않은 변경사항이 있습니다.
    echo 먼저 git add와 git commit을 완료한 뒤 다시 실행해 주세요.
    git status --short
    pause
    exit /b 1
)

git rev-parse "v%APP_VERSION%" >nul 2>nul && (
    echo v%APP_VERSION% 태그가 이미 존재합니다.
    echo 새 배포라면 dakknyang\__init__.py의 버전을 올려 주세요.
    pause
    exit /b 1
)

echo 현재 커밋을 원격 저장소에 올립니다.
git push origin HEAD || goto :error

echo v%APP_VERSION% 태그를 만들고 배포를 시작합니다.
git tag -a "v%APP_VERSION%" -m "잠깐닦냥 v%APP_VERSION%"
git push origin "v%APP_VERSION%" || goto :error

echo.
echo GitHub Actions가 Windows 실행 파일을 자동으로 만들고 있습니다.
echo 저장소의 Actions 또는 Releases 화면에서 진행 상태를 확인하세요.
pause
exit /b 0

:error
echo 배포 요청에 실패했습니다. Git 원격 저장소와 로그인 상태를 확인해 주세요.
pause
exit /b 1


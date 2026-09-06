# 잠깐닦냥

키보드와 마우스를 닦는 동안 실수로 다른 프로그램을 조작하지 않도록 전체 화면으로 보호하는 Windows용 Python 데스크톱 앱입니다. v0.1.0의 주인공은 고양이이며, 이후 버전에서 강아지와 다람쥐 등 새로운 동물과 기능을 추가할 예정입니다.

## 현재 MVP 기능

- 전체 화면, 항상 위 오버레이
- 외부 이미지 없이 직접 그린 고양이 캐릭터
- `캐릭터 클릭 → 스페이스바 5회`의 2단계 해제
- 키를 길게 누르는 자동 반복은 횟수에서 제외
- 60초 후 자동 해제되는 안전 타이머
- 청소 모드 동안 왼쪽·오른쪽 Windows 키 차단
- UI와 분리된 해제 상태 로직 및 단위 테스트

> 현재 버전은 전체 화면 창이 대부분의 입력을 받고, Windows 키만 저수준 후크로 차단합니다. `Ctrl+Alt+Delete`는 Windows 보안 정책상 일반 프로그램이 차단할 수 없으며 비상 탈출 수단으로 유지됩니다.

## 기술 구성

### Python

앱의 실행 흐름, 타이머, 해제 규칙을 작성하는 주 언어입니다. 기존 Python 경험을 활용해 빠르게 완성하고, 이후 LLM Agent 프로젝트에서도 같은 언어를 이어서 사용할 수 있습니다.

### PySide6

Qt라는 데스크톱 GUI 프레임워크의 공식 Python 바인딩입니다. 이 프로젝트에서는 실행 창, 전체 화면 오버레이, 버튼, 글자, 타이머와 캐릭터 그리기를 담당합니다. Tkinter보다 설치 용량은 크지만 화면 구성과 확장성이 좋습니다.

### Qt 이벤트 시스템

Windows API를 직접 호출하기 전 단계로, PySide6가 전달하는 키보드·마우스 이벤트를 처리합니다. `keyPressEvent()`에서 스페이스바만 해제 동작에 사용하고 나머지 키 입력은 오버레이 내부에서 소비합니다.

### Windows API와 `ctypes`

Windows 키는 운영체제가 먼저 처리하기 때문에 PySide6 이벤트만으로 확실하게 막기 어렵습니다. Python 표준 라이브러리인 `ctypes`로 Windows DLL 함수를 호출해 청소 모드 동안 저수준 키보드 후크를 설치합니다.

- `SetWindowsHookExW`: `WH_KEYBOARD_LL` 후크를 등록해 키보드 입력을 먼저 확인합니다.
- `CallNextHookEx`: 차단 대상이 아닌 입력을 정상적인 다음 처리 단계로 전달합니다.
- `UnhookWindowsHookEx`: 청소 모드가 끝날 때 후크를 제거합니다.
- `GetModuleHandleW`: 현재 실행 프로그램의 모듈 핸들을 가져옵니다.

후크 콜백은 왼쪽 Windows 키(`VK_LWIN`)와 오른쪽 Windows 키(`VK_RWIN`)에만 `1`을 반환해 전달을 중단합니다. 스페이스바를 포함한 나머지 키는 그대로 전달되므로 PySide6 화면에서 해제 동작을 받을 수 있습니다.

### pytest

화면과 무관한 해제 규칙을 자동 검증합니다. 캐릭터를 클릭하기 전에는 스페이스바가 무시되는지, 필요한 횟수에서만 해제되는지 등을 테스트합니다.

## 개발 환경 실행

Windows PowerShell 기준입니다.

```powershell
cd jamkkan-daknyang
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python main.py
```

테스트 실행:

```powershell
python -m pytest
```

## 사용 방법

1. `청소 모드 시작` 버튼을 누릅니다.
2. 키보드와 마우스를 닦습니다.
3. 화면 중앙의 고양이를 클릭합니다.
4. 스페이스바를 한 번씩 5회 누릅니다.
5. 해제되면 시작 화면으로 돌아옵니다.

## 다음 개발 단계

1. Windows와 다중 모니터에서 실제 동작 테스트
2. PyInstaller를 이용한 `잠깐닦냥.exe` 패키징
3. 해제 횟수와 자동 해제 시간 설정 화면
4. 강아지·다람쥐 캐릭터 선택과 캐릭터별 애니메이션
5. 시스템 트레이 및 단축키 시작
6. `Alt+Tab` 등 추가 시스템 단축키의 차단 범위 검토

## 버전 로드맵

| 버전 | 캐릭터 | 목표 기능 |
| --- | --- | --- |
| v0.1.0 | 고양이 | 전체 화면 보호, 2단계 해제, Windows 키 차단, 자동 해제 |
| v0.2.0 | 고양이 | 실행 파일 배포, 설정 화면, 트레이 실행 |
| v0.3.0 | 고양이·강아지·다람쥐 | 캐릭터 선택, 테마와 애니메이션 |

저수준 후크는 Windows 키에만 제한했습니다. 모든 키를 전역 차단하면 오류 발생 시 컴퓨터 조작이 어려워질 수 있으므로, 자동 타이머와 `Ctrl+Alt+Delete` 비상 탈출 수단은 그대로 유지합니다.

## 사용자가 프로그램만 다운로드하게 만들기

PyInstaller는 Python 코드와 Python 실행 환경, PySide6, 필요한 DLL을 Windows 실행 파일에 함께 묶습니다. 사용자는 Python을 설치하지 않고 `잠깐닦냥.exe`만 실행할 수 있습니다.

Windows에서 `build.bat`을 더블클릭하면 다음 과정이 자동으로 수행됩니다.

1. `.venv`가 없으면 가상환경 생성
2. PySide6, pytest, PyInstaller 설치
3. 단위 테스트 실행
4. 단일 GUI 실행 파일 생성
5. `dist` 폴더 열기

완성된 파일:

```text
dist\잠깐닦냥.exe
```

`--onefile`은 라이브러리를 EXE 안에 포함하고, `--windowed`는 실행할 때 검은 CMD 창이 나타나지 않게 합니다. 첫 실행 때 내부 파일을 임시 디렉터리에 풀기 때문에 시작이 약간 느릴 수 있습니다.

## GitHub 자동 배포

`.github/workflows/release.yml`은 GitHub Actions라는 자동 실행 환경의 작업 명세입니다. `v0.1.0` 같은 Git 태그가 올라오면 GitHub의 Windows 서버가 다음 작업을 대신 수행합니다.

```text
태그 감지 → Windows 환경 준비 → 의존성 설치 → 테스트
→ 잠깐닦냥.exe 빌드 → GitHub Release 생성 → EXE 첨부
```

최초 한 번 GitHub 저장소에 프로젝트를 연결하고 커밋한 뒤, 새 버전에서는 다음 두 가지만 하면 됩니다.

1. `dakknyang\__init__.py`의 `__version__` 변경
2. 변경사항을 커밋하고 `release.bat` 더블클릭

`release.bat`은 작업 내용이 모두 커밋되었는지 검사한 다음 현재 버전의 태그를 생성해 GitHub에 전송합니다. 이후 EXE 생성과 Releases 게시 작업은 GitHub Actions가 처리합니다. 같은 버전 태그가 이미 존재하면 실수로 덮어쓰지 않고 중단합니다.

GitHub 저장소의 **Settings → Actions → General → Workflow permissions**에서 `Read and write permissions`가 허용되어야 Release를 만들 수 있습니다. 조직 정책으로 쓰기가 제한된 저장소에서는 관리자 설정이 필요할 수 있습니다.

태그 없이 자동 빌드만 시험하려면 GitHub 저장소의 **Actions → Build and release Windows app → Run workflow**를 실행합니다. 이 경우 Actions의 Artifacts에서 EXE를 받을 수 있지만 정식 Release는 생성하지 않습니다.

# 펌웨어 격리 빌드 도구

`Build-Firmware.ps1`은 기존 `stm32_uart_mvp/Debug`,
`stm32_uart_mvp/Release`, `esp32_uart_bridge/build`를 수정하지 않고 STM32와
ESP32 펌웨어를 빌드한다.

각 소스 트리를 `%TEMP%\tmr-fw` 아래의 짧고 고유한 경로로 복사하여 빌드하고, 로그와 주요
바이너리는 저장소 밖의 다음 경로에 보존한다.

```text
%LOCALAPPDATA%\TrackedMobileRobot\builds\<run-id>
```

보드 플래시는 수행하지 않는다.

## 실행

PowerShell 7(`pwsh`)에서 저장소 루트 `TIL`을 기준으로
`03_Firmware/tools`로 이동해 실행한다. Windows PowerShell 5.1은 이
스크립트의 경로 검증 API를 지원하지 않는다.

```powershell
pwsh
Set-Location Projects\Tracked_Mobile_Robot\03_Firmware\tools
.\Build-Firmware.ps1
```

주요 옵션은 다음과 같다.

```powershell
# 한 종류만 빌드
.\Build-Firmware.ps1 -Target STM32
.\Build-Firmware.ps1 -Target ESP32

# STM32 Release 구성 빌드
.\Build-Firmware.ps1 -Target STM32 -Configuration Release

# 프로젝트에 tracked/untracked 변경이 있으면 중단
.\Build-Firmware.ps1 -RequireClean

# 성공 후에도 임시 격리 소스와 빌드 폴더 보존
.\Build-Firmware.ps1 -KeepStage
```

스크립트가 설치 도구를 자동 탐지한다. 현재 노트북의 기본 경로는 `C:\ST`의
STM32CubeIDE 2.1.1과 `C:\esp`/`C:\Espressif`의 ESP-IDF 6.0.2다. 필요하면
다음처럼 경로를 직접 지정한다.

```powershell
.\Build-Firmware.ps1 `
  -CubeIdeHeadlessPath "C:\path\to\headless-build.bat" `
  -EspIdfProfilePath "C:\path\to\PowerShell_profile.ps1" `
  -EspPythonPath "C:\path\to\python.exe" `
  -IdfPyPath "C:\path\to\idf.py"
```

이 노트북에서는 설치 관리자가 생성한 ESP-IDF PowerShell profile이 Python과
toolchain 경로를 선택한다. 이 profile을 일반 `esp-idf\export.ps1`로 대체하지
않는다.

실패하면 non-zero 오류를 반환하고 staging 트리를 보존하며, 해당 실행의 artifact
폴더에 `failure.txt`와 생성된 로그를 남긴다. `-RequireClean`은 이 스크립트와
빌드할 펌웨어 변경을 커밋한 뒤 사용하는 것이 적절하다.

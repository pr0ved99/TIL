# UART MVP 실행 가이드

## 목적

이 문서는 STM32와 PC를 USB로 연결해 UART MVP를 실행하는 순서를 한 번에 보기 위한 runbook이다.

실행 대상은 두 가지다.

1. Web Serial Dashboard
2. Terminal UART Tool

권장 순서는 다음이다.

```text
1. STM32 firmware 준비 전: Web dashboard Fake TEL로 UI 확인
2. STM32 firmware 준비 후: Web dashboard 또는 terminal tool로 실제 UART 확인
3. Evidence 저장: raw log, CSV, screenshot
```

## 전체 구조

```text
PC Browser / Terminal Tool
<-> ST-LINK Virtual COM Port
<-> STM32 USART2
<-> UART MVP parser
<-> ACK / ERR / TEL response
```

이번 MVP에서 연결하지 않는 것:

- MDD10A motor power
- DC motor
- 3S LiPo battery
- buck converter output

이번 MVP에서 확인하는 것:

- `PING` -> `PONG`
- `ARM` -> `ACK`
- valid `CMD` -> `ACK`
- invalid `CMD` -> `ERR`
- periodic `TEL`
- timeout 후 output zero telemetry
- `DISARM` -> `ACK`, `TEL,state=DISARMED`

## 실행 전 체크리스트

### 공통

- NUCLEO-F446RE를 PC에 USB로 연결한다.
- USB cable이 data cable인지 확인한다.
- STM32 firmware는 USART2 115200 8N1로 설정한다.
- STM32 response frame은 `\n`으로 끝나야 한다.
- STM32CubeProgrammer, Tera Term, PuTTY, Serial Monitor 등 같은 port를 잡는 프로그램은 닫는다.

### STM32 firmware가 아직 없을 때

할 수 있는 것:

- Web dashboard 실행
- `Fake TEL`로 UI 확인
- raw frame parse 확인
- CSV download 확인

할 수 없는 것:

- 실제 `Connect` 후 `PONG`, `ACK`, `ERR`, `TEL` 수신 검증

### STM32 firmware가 있을 때

할 수 있는 것:

- Web Serial로 실제 ST-LINK VCP 연결
- Terminal tool로 scripted smoke test 실행
- UART log를 evidence로 저장

## Windows 실행: Web Dashboard

### 1. 서버 실행

PowerShell:

```powershell
cd C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\04_PC_Serial_Control
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ServeWebDashboard.ps1
```

정상 출력 예:

```text
Serving ...
Open http://localhost:8765/
Press Ctrl+C to stop.
```

### 2. 브라우저 열기

Chrome 또는 Edge에서 연다.

```text
http://localhost:8765/
```

### 3. STM32 연결

1. baud rate를 `115200`으로 둔다.
2. `Connect`를 누른다.
3. ST-LINK Virtual COM Port를 선택한다.
4. `Connection`이 `CONNECTED`로 바뀌는지 확인한다.

### 4. 기본 검증

순서:

1. `PING`
2. `CMD`
3. `ARM`
4. `CMD`
5. `Bad Range`
6. `Keepalive`
7. `DISARM`

기대 결과:

| Action | Expected |
| --- | --- |
| `PING` | `PONG,seq=...` |
| `CMD` before `ARM` | `ERR,code=NOT_ARMED` |
| `ARM` | `ACK,type=ARM`, later `TEL,state=ARMED` |
| valid `CMD` | `ACK,type=CMD` |
| `Bad Range` | `ERR,code=OUT_OF_RANGE` |
| stop keepalive | `TEL`에서 output zero 확인 |
| `DISARM` | `ACK,type=DISARM`, later `TEL,state=DISARMED` |

### 5. CSV 저장

대시보드에서 `CSV` 버튼을 누르면 현재 browser memory에 쌓인 TX/RX log를 CSV로 저장한다.

## Windows 실행: Terminal Tool

### 1. Port 확인

```powershell
cd C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\04_PC_Serial_Control
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode ListPorts
```

예:

```text
COM5
```

### 2. Interactive 실행

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Interactive -Port COM5
```

### 3. Scripted smoke test

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode ScriptedTest -Port COM5
```

Log 위치:

```text
04_PC_Serial_Control/logs/
```

생성 파일:

```text
uart_mvp_YYYYMMDD_HHMMSS_raw.log
uart_mvp_YYYYMMDD_HHMMSS_parsed.csv
```

## Ubuntu 실행: Web Dashboard

### 1. 서버 실행

```bash
cd ~/workspace/TIL/Projects/Tracked_Mobile_Robot/04_PC_Serial_Control
bash tools/serve_web_dashboard.sh
```

### 2. 브라우저 열기

Chrome 또는 Edge:

```text
http://localhost:8765/
```

### 3. Serial 권한 확인

ST-LINK VCP는 보통 `/dev/ttyACM0`로 잡힌다.

```bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

권한 문제가 있으면:

```bash
sudo usermod -aG dialout "$USER"
```

로그아웃 후 다시 로그인한다.

## Ubuntu 실행: Terminal Tool

### 1. Port 확인

```bash
cd ~/workspace/TIL/Projects/Tracked_Mobile_Robot/04_PC_Serial_Control
bash tools/uart_mvp_tool.sh list-ports
```

예:

```text
/dev/ttyACM0
```

### 2. Interactive 실행

```bash
bash tools/uart_mvp_tool.sh interactive --port /dev/ttyACM0
```

### 3. Scripted smoke test

```bash
bash tools/uart_mvp_tool.sh scripted-test --port /dev/ttyACM0
```

## 성공 기준

다음 evidence가 있으면 PC-first UART MVP 실행 성공으로 본다.

| Evidence | Required |
| --- | --- |
| `PING` -> `PONG` | Yes |
| `ARM` -> `ACK` | Yes |
| valid `CMD` -> `ACK` | Yes |
| missing field `CMD` -> `ERR,code=MISSING_FIELD` | Yes |
| out-of-range `CMD` -> `ERR,code=OUT_OF_RANGE` | Yes |
| `DISARMED` 상태 nonzero `CMD` -> `ERR,code=NOT_ARMED` | Yes |
| timeout 후 output zero telemetry | Yes |
| `DISARM` -> `ACK`, `TEL,state=DISARMED` | Yes |
| raw log 또는 dashboard screenshot | Yes |
| parsed CSV | Recommended |

## Troubleshooting

### Web dashboard의 Connect 버튼이 비활성화됨

원인:

- Chrome/Edge가 아님
- `file://`로 열었음
- `localhost`가 아닌 경로로 열었음

해결:

```text
http://localhost:8765/
```

으로 연다.

### Port가 안 보임

확인:

- USB cable이 data cable인지
- 다른 serial monitor가 port를 잡고 있는지
- Windows Device Manager에서 ST-LINK VCP가 보이는지
- Ubuntu에서 `/dev/ttyACM0`가 생겼는지

### TX는 보이는데 RX가 없음

가능한 원인:

- STM32 firmware가 아직 UART MVP response를 구현하지 않음
- USART2가 아니라 다른 UART를 설정함
- baud rate mismatch
- STM32 response에 `\n`이 없음
- `HAL_UART_Receive_IT()` 재등록 누락

### ERR code가 기대와 다름

STM32 parser의 error priority를 확인한다.

권장 우선순위:

```text
BAD_FRAME
UNKNOWN_TYPE
MISSING_FIELD
BAD_VALUE
OUT_OF_RANGE
NOT_ARMED
FAULT_ACTIVE
```

## 다음 단계

1. STM32 firmware guide를 따라 USART2 parser를 구현한다.
2. Web dashboard `Fake TEL`로 UI를 먼저 확인한다.
3. 실제 ST-LINK VCP에 연결해 `PING/PONG`부터 확인한다.
4. Scripted smoke test를 실행한다.
5. `logs/` 또는 dashboard CSV를 evidence로 저장한다.
6. 검증 결과를 hardware validation 또는 progress 문서에 요약한다.

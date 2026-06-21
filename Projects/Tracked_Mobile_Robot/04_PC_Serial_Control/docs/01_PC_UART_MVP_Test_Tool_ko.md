# PC UART MVP Test Tool

## Purpose

이 문서는 PC에서 STM32 NUCLEO-F446RE를 USB로 연결한 뒤 UART MVP rule을 검증하는 방법을 정의한다.

목표는 모터, MDD10A, LiPo 전원 없이 다음을 먼저 증명하는 것이다.

- PC가 MVP frame을 구성해 STM32로 보낸다.
- STM32가 `PING`, `ARM`, `DISARM`, `CMD`를 parsing한다.
- STM32가 rule에 맞게 `PONG`, `ACK`, `ERR`, `TEL`을 보낸다.
- PC가 raw RX/TX log와 parsed CSV log를 남긴다.

## Folder Layout

```text
04_PC_Serial_Control/
  README.md
  requirements.txt
  tools/
    UartMvpTool.ps1
    uart_mvp_tool.sh
    uart_mvp_tool.py
  tests/
    test_uart_mvp_tool.py
  logs/
    .gitkeep
  docs/
    01_PC_UART_MVP_Test_Tool_ko.md
    02_STM32_UART_MVP_Firmware_Guide_ko.md
    03_Ubuntu_UART_MVP_Test_Tool_ko.md
```

## Safety Scope

이번 실습에서는 다음을 연결하지 않는다.

- MDD10A motor power
- DC motor
- 3S LiPo battery
- buck converter output

허용하는 연결:

```text
PC USB
<-> NUCLEO-F446RE ST-LINK USB
<-> ST-LINK Virtual COM Port
<-> STM32 USART2
```

즉, 이번 실습은 UART protocol, parser, response, telemetry만 확인한다.

## Recommended Tool On Windows

현재 Windows PowerShell 환경에서는 `tools/UartMvpTool.ps1`을 1순위 도구로 사용한다.
이 도구는 별도 Python 설치 없이 .NET SerialPort를 사용한다.

PowerShell execution policy 때문에 script 실행이 막히면 다음 형식으로 실행한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Build -Frame PING -Seq 1
```

Python version인 `tools/uart_mvp_tool.py`도 같이 제공하지만, Python과 `pyserial`이 설치된 환경에서만 사용한다.

## Optional Python Install

PowerShell에서 `04_PC_Serial_Control` 폴더로 이동한다.

```powershell
cd C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\04_PC_Serial_Control
python -m pip install -r requirements.txt
```

Python 명령이 동작하지 않으면 Windows Python launcher를 사용한다.

```powershell
py -m pip install -r requirements.txt
```

## Find Serial Port

NUCLEO-F446RE를 PC에 USB로 연결한 뒤 port를 확인한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode ListPorts
```

예상 출력 예:

```text
COM5    STMicroelectronics STLink Virtual COM Port
```

이후 예시는 `COM5`라고 가정한다.

## Dry Run

하드웨어 연결 전에도 frame 생성은 확인할 수 있다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Build -Frame PING -Seq 1
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Build -Frame ARM -Seq 2
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Build -Frame CMD -Seq 3 -VxMmps 80 -WMradps 0 -TimeoutMs 300
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Build -Frame DISARM -Seq 4
```

예상 출력:

```text
CMD,seq=3,vx_mmps=80,w_mradps=0,timeout_ms=300
```

## Single Frame Send

`PING` 전송:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Send -Port COM5 -Frame PING -Seq 1
```

기대 RX:

```text
PONG,seq=1,t_ms=...
```

`ARM` 전송:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Send -Port COM5 -Frame ARM -Seq 2
```

기대 RX:

```text
ACK,seq=2,type=ARM
TEL,...,state=ARMED,...
```

valid `CMD` 전송:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Send -Port COM5 -Frame CMD -Seq 3 -VxMmps 80 -WMradps 0 -TimeoutMs 300
```

기대 RX:

```text
ACK,seq=3,type=CMD
```

out-of-range `CMD` 전송:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Send -Port COM5 -Frame RAW -Raw "CMD,seq=4,vx_mmps=9999,w_mradps=0,timeout_ms=300"
```

기대 RX:

```text
ERR,seq=4,type=CMD,code=OUT_OF_RANGE
```

## Interactive Mode

가장 추천하는 실습 방식은 interactive mode다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Interactive -Port COM5
```

메뉴:

```text
1) PING
2) ARM
3) DISARM
4) CMD custom
5) CMD zero once
6) zero-CMD keepalive
7) raw frame
8) out-of-range CMD
9) monitor wait
q) quit
```

실습 순서:

1. `PING`을 보내 `PONG`이 오는지 확인한다.
2. `CMD custom`으로 nonzero command를 보낸다. 초기 `DISARMED` 상태라면 `ERR,code=NOT_ARMED`가 와야 한다.
3. `ARM`을 보낸다.
4. valid `CMD`를 보낸다. `ACK,type=CMD`가 와야 한다.
5. `out-of-range CMD`를 보낸다. `ERR,code=OUT_OF_RANGE`가 와야 한다.
6. `zero-CMD keepalive`를 3초 정도 실행한다.
7. keepalive를 멈추고 `TEL`에서 output zero 또는 timeout 상태가 보이는지 확인한다.
8. `DISARM`을 보내고 `TEL,state=DISARMED`를 확인한다.

## Scripted Smoke Test

반복 검증용 sequence를 자동으로 보낼 수 있다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode ScriptedTest -Port COM5
```

전송 sequence:

```text
PING,seq=1
CMD,seq=2,vx_mmps=80,w_mradps=0,timeout_ms=300
ARM,seq=3
CMD,seq=4,vx_mmps=80,w_mradps=0,timeout_ms=300
CMD,seq=5,vx_mmps=80,timeout_ms=300
CMD,seq=6,vx_mmps=9999,w_mradps=0,timeout_ms=300
CMD,seq=7,vx_mmps=0,w_mradps=0,timeout_ms=300
DISARM,seq=8
```

기대 반응:

| TX | Expected RX |
| --- | --- |
| `PING` | `PONG` |
| `CMD` while `DISARMED` | `ERR,code=NOT_ARMED` |
| `ARM` | `ACK,type=ARM` |
| valid `CMD` | `ACK,type=CMD` |
| missing field `CMD` | `ERR,code=MISSING_FIELD` |
| out-of-range `CMD` | `ERR,code=OUT_OF_RANGE` |
| `DISARM` | `ACK,type=DISARM`, later `TEL,state=DISARMED` |

Dry run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode ScriptedTest -DryRun
```

## Monitor Only

STM32가 주기적으로 `TEL`을 보내는지만 보고 싶을 때:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\UartMvpTool.ps1 -Mode Monitor -Port COM5
```

중단은 `Ctrl+C`.

## Log Files

기본 log 위치:

```text
04_PC_Serial_Control/logs/
```

생성 파일:

```text
uart_mvp_YYYYMMDD_HHMMSS_raw.log
uart_mvp_YYYYMMDD_HHMMSS_parsed.csv
```

Raw log 예:

```text
2026-06-21T20:30:10.123+09:00 TX PING,seq=1
2026-06-21T20:30:10.130+09:00 RX PONG,seq=1,t_ms=5432
```

Parsed CSV field:

| Column | Meaning |
| --- | --- |
| `timestamp` | PC receive/send time |
| `direction` | `TX` 또는 `RX` |
| `frame_type` | `PING`, `ACK`, `ERR`, `TEL` 등 |
| `seq` | sequence number |
| `state` | telemetry state |
| `code` | error code |
| `category` | `accepted`, `rejected`, `telemetry`, `pong` 등 |
| `raw` | 원본 line |

## MVP Pass Criteria

이번 PC UART MVP는 다음이 log로 남으면 통과로 본다.

- `PING` -> `PONG`
- `ARM` -> `ACK`
- valid `CMD` -> `ACK`
- missing field `CMD` -> `ERR,code=MISSING_FIELD`
- out-of-range `CMD` -> `ERR,code=OUT_OF_RANGE`
- `DISARMED` 상태 nonzero `CMD` -> `ERR,code=NOT_ARMED`
- command timeout 이후 `TEL`에서 output zero 확인
- `DISARM` -> `ACK` 및 이후 `TEL,state=DISARMED`

## Troubleshooting

### Port가 안 보임

- NUCLEO USB cable이 data cable인지 확인한다.
- Windows Device Manager에서 ST-LINK Virtual COM Port를 확인한다.
- STM32CubeProgrammer 또는 CubeIDE가 같은 COM port를 잡고 있으면 닫는다.

### TX는 되는데 RX가 안 보임

- STM32 firmware에서 USART2 TX/RX가 활성화됐는지 확인한다.
- `HAL_UART_Receive_IT()` 재등록이 빠지지 않았는지 확인한다.
- STM32가 `\n`으로 line을 끝내고 있는지 확인한다.

### 글자가 깨짐

- 양쪽 baud rate가 115200인지 확인한다.
- parity/stop bit 설정이 8N1인지 확인한다.

### `ERR`가 기대와 다름

- STM32 parser의 error 우선순위를 확인한다.
- 예를 들어 missing field를 먼저 검사하면 `MISSING_FIELD`, 숫자 변환을 먼저 검사하면 `BAD_VALUE`가 나올 수 있다.
  MVP에서는 우선순위를 문서와 firmware에 맞춰 고정해야 한다.

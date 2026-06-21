# Ubuntu UART MVP Test Tool

## Purpose

이 문서는 Ubuntu PC에서 STM32 NUCLEO-F446RE를 USB로 연결한 뒤 UART MVP rule을 검증하는 방법을 정의한다.

Ubuntu에서는 ST-LINK Virtual COM Port가 보통 다음 device로 잡힌다.

```text
/dev/ttyACM0
```

USB-UART adapter를 별도로 쓰면 보통 다음 device로 잡힌다.

```text
/dev/ttyUSB0
```

이번 프로젝트의 PC-first MVP는 ST-LINK VCP를 우선 사용한다.

## Tool

Ubuntu용 도구:

```text
tools/uart_mvp_tool.sh
```

기능:

- serial port 목록 확인
- MVP frame 생성
- 단일 frame 송신
- RX monitoring
- interactive command console
- scripted MVP smoke test
- raw log와 parsed CSV log 저장

## Safety Scope

이번 실습에서는 다음을 연결하지 않는다.

- MDD10A motor power
- DC motor
- 3S LiPo battery
- buck converter output

허용 연결:

```text
Ubuntu PC USB
<-> NUCLEO-F446RE ST-LINK USB
<-> ST-LINK Virtual COM Port
<-> STM32 USART2
```

## Package Check

대부분의 Ubuntu 기본 설치에는 `bash`, `stty`, `awk`, `date`가 이미 있다.

필요 시:

```bash
sudo apt update
sudo apt install coreutils gawk
```

Python이 있는 Ubuntu라면 `tools/uart_mvp_tool.py`도 사용할 수 있지만, 이 문서는 shell script를 기준으로 한다.

## Serial Permission

NUCLEO를 USB로 연결한 뒤 device를 확인한다.

```bash
cd ~/workspace/TIL/Projects/Tracked_Mobile_Robot/04_PC_Serial_Control
bash tools/uart_mvp_tool.sh list-ports
```

예상:

```text
/dev/ttyACM0
/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_... -> /dev/ttyACM0
```

권한 에러가 나면 현재 사용자를 `dialout` group에 추가한다.

```bash
sudo usermod -aG dialout "$USER"
```

그 다음 **로그아웃 후 다시 로그인**해야 group 권한이 반영된다.

임시 테스트만 할 경우:

```bash
sudo chmod a+rw /dev/ttyACM0
```

이 방법은 재부팅 또는 재연결 후 다시 풀릴 수 있으므로 장기적으로는 `dialout` group을 사용한다.

## Dry Run

하드웨어 없이 frame 생성만 확인한다.

```bash
bash tools/uart_mvp_tool.sh build PING --seq 1
bash tools/uart_mvp_tool.sh build ARM --seq 2
bash tools/uart_mvp_tool.sh build CMD --seq 3 --vx-mmps 80 --w-mradps 0 --timeout-ms 300
bash tools/uart_mvp_tool.sh build DISARM --seq 4
```

예상:

```text
CMD,seq=3,vx_mmps=80,w_mradps=0,timeout_ms=300
```

Scripted test dry run:

```bash
bash tools/uart_mvp_tool.sh scripted-test --dry-run
```

## Single Frame Send

`PING`:

```bash
bash tools/uart_mvp_tool.sh send --port /dev/ttyACM0 PING --seq 1
```

기대 RX:

```text
PONG,seq=1,t_ms=...
```

`ARM`:

```bash
bash tools/uart_mvp_tool.sh send --port /dev/ttyACM0 ARM --seq 2
```

기대 RX:

```text
ACK,seq=2,type=ARM
TEL,...,state=ARMED,...
```

valid `CMD`:

```bash
bash tools/uart_mvp_tool.sh send --port /dev/ttyACM0 CMD --seq 3 --vx-mmps 80 --w-mradps 0 --timeout-ms 300
```

기대 RX:

```text
ACK,seq=3,type=CMD
```

out-of-range `CMD`:

```bash
bash tools/uart_mvp_tool.sh send --port /dev/ttyACM0 RAW --raw "CMD,seq=4,vx_mmps=9999,w_mradps=0,timeout_ms=300"
```

기대 RX:

```text
ERR,seq=4,type=CMD,code=OUT_OF_RANGE
```

## Interactive Mode

추천 실습 방식:

```bash
bash tools/uart_mvp_tool.sh interactive --port /dev/ttyACM0
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

권장 실습 순서:

1. `PING`으로 `PONG` 확인
2. `DISARMED` 상태에서 nonzero `CMD`를 보내 `ERR,code=NOT_ARMED` 확인
3. `ARM`으로 `ACK,type=ARM` 확인
4. valid `CMD`로 `ACK,type=CMD` 확인
5. out-of-range `CMD`로 `ERR,code=OUT_OF_RANGE` 확인
6. zero-CMD keepalive를 3초 실행
7. keepalive 중단 후 timeout zero-output telemetry 확인
8. `DISARM` 후 `TEL,state=DISARMED` 확인

## Scripted Smoke Test

반복 검증용 sequence:

```bash
bash tools/uart_mvp_tool.sh scripted-test --port /dev/ttyACM0
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

## Monitor Only

STM32가 주기적으로 `TEL`을 보내는지만 확인:

```bash
bash tools/uart_mvp_tool.sh monitor --port /dev/ttyACM0
```

중단:

```text
Ctrl+C
```

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

Parsed CSV:

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

## Troubleshooting

### `/dev/ttyACM0`가 없음

확인:

```bash
dmesg | tail -n 50
lsusb
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

가능한 원인:

- USB cable이 charge-only cable
- ST-LINK driver/device 인식 문제
- STM32 board가 reset 중이거나 USB가 불안정

### Permission denied

해결:

```bash
sudo usermod -aG dialout "$USER"
```

로그아웃 후 다시 로그인한다.

### Port busy

다른 프로그램이 serial device를 잡고 있는지 확인한다.

```bash
sudo lsof /dev/ttyACM0
```

예:

- minicom
- screen
- STM32CubeProgrammer
- serial monitor

### 글자가 깨짐

확인:

- STM32 USART2 baud rate: 115200
- PC tool baud rate: 115200
- 8 data bits, no parity, 1 stop bit
- STM32 response가 `\n`으로 끝나는지

## MVP Pass Criteria

Ubuntu PC UART MVP도 Windows와 동일하게 다음 log가 확보되면 통과로 본다.

- `PING` -> `PONG`
- `ARM` -> `ACK`
- valid `CMD` -> `ACK`
- missing field `CMD` -> `ERR,code=MISSING_FIELD`
- out-of-range `CMD` -> `ERR,code=OUT_OF_RANGE`
- `DISARMED` 상태 nonzero `CMD` -> `ERR,code=NOT_ARMED`
- command timeout 이후 `TEL`에서 output zero 확인
- `DISARM` -> `ACK` 및 이후 `TEL,state=DISARMED`

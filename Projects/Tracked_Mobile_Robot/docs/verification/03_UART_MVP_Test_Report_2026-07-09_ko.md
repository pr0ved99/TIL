# UART MVP Test Report - 2026-07-09

## Summary

2026-07-09에 NUCLEO-F446RE와 PC Web Serial dashboard를 사용해 UART MVP를 검증했다.

결론:

```text
PC-first UART MVP PASS
```

검증된 사항:

- STM32와 PC dashboard가 ST-LINK VCP로 연결된다.
- STM32가 periodic telemetry를 송신한다.
- `PING/PONG` health check가 동작한다.
- `DISARMED` 상태에서 `CMD`는 `NOT_ARMED`로 거부된다.
- `ARM` 후 valid `CMD`가 ACK된다.
- valid `CMD`의 velocity가 telemetry에 반영된다.
- `timeout_ms=500` 이후 velocity command가 zero로 떨어진다.
- 잘못된 velocity range는 `OUT_OF_RANGE`로 거부된다.
- `DISARM` 후 `DISARMED` 상태로 복귀한다.

## Test Environment

| Item | Value |
| --- | --- |
| Date | 2026-07-09 |
| MCU board | NUCLEO-F446RE |
| Firmware project | `03_Firmware/stm32_uart_mvp` |
| PC dashboard | `04_PC_Serial_Control/web_serial_dashboard` |
| Serial path | ST-LINK Virtual COM Port |
| UART setting | 115200 8N1 |
| Browser | Chrome / Edge Web Serial compatible browser |
| Motor driver | Not connected |
| Motor power | Not connected |

## Test Procedure

1. Build and flash STM32 UART MVP firmware.
2. Open Web Serial dashboard at `http://localhost:8765/`.
3. Connect to ST-LINK Virtual COM Port at `115200`.
4. Observe periodic `TEL`.
5. Send `PING`.
6. Send `CMD` before `ARM`.
7. Send `ARM`.
8. Send valid `CMD` with `vx_mmps=50`, `w_mradps=0`, `timeout_ms=500`.
9. Wait longer than `timeout_ms`.
10. Send invalid range `CMD`.
11. Send `DISARM`.
12. Export dashboard CSV.
13. Save screenshots.

## Evidence

### EV-01: Connected idle

![Connected idle](../../assets/screenshots/uart_mvp/2026-07-09_01_web_dashboard_connected_idle.png)

Observation:

- `CONNECTION=CONNECTED`
- `ROBOT=DISARMED`
- periodic `TEL` received

### EV-02: PING/PONG

![PING PONG](../../assets/screenshots/uart_mvp/2026-07-09_02_ping_pong_response.png)

Observation:

- `LAST TX = PING,seq=1`
- `LAST ACK = PONG,seq=1`

### EV-03: CMD before ARM rejected

![CMD before ARM](../../assets/screenshots/uart_mvp/2026-07-09_03_cmd_before_arm_not_armed_error.png)

Observation:

- `ROBOT=DISARMED`
- `LAST TX = CMD,seq=2,...`
- `LAST ERR = ERR,seq=2,type=CMD,code=NOT_ARMED`

### EV-04: ARM accepted

![ARM ACK](../../assets/screenshots/uart_mvp/2026-07-09_04_arm_ack_state_armed.png)

Observation:

- `LAST TX = ARM,seq=3`
- `LAST ACK = ACK,seq=3,type=ARM`
- `ROBOT=ARMED`

### EV-05: Valid CMD accepted

![Valid CMD ACK](../../assets/screenshots/uart_mvp/2026-07-09_05_valid_cmd_ack_armed.png)

Observation:

- `LAST TX = CMD,seq=20,vx_mmps=50,w_mradps=0,timeout_ms=500`
- `LAST ACK = ACK,seq=20,type=CMD`
- `LAST RX` includes `vx_mmps=50`

### EV-06: Timeout output zero

![Timeout output zero](../../assets/screenshots/uart_mvp/2026-07-09_06_cmd_timeout_output_zero.png)

Observation:

- last accepted command remains `seq=20`
- telemetry changes from `vx_mmps=50` to `vx_mmps=0`
- `ROBOT=ARMED`, but output command is zero

### EV-07: Bad range rejected

![Bad range](../../assets/screenshots/uart_mvp/2026-07-09_07_bad_range_out_of_range_error.png)

Observation:

- `LAST TX = CMD,seq=25,vx_mmps=9999,...`
- `LAST ERR = ERR,seq=25,type=CMD,code=OUT_OF_RANGE`

### EV-08: DISARM accepted

![DISARM ACK](../../assets/screenshots/uart_mvp/2026-07-09_08_disarm_ack_state_disarmed.png)

Observation:

- `LAST TX = DISARM,seq=26`
- `LAST ACK = ACK,seq=26,type=DISARM`
- `ROBOT=DISARMED`

### EV-CSV: Full UART session log

CSV evidence:

[`../../04_PC_Serial_Control/logs/2026-07-09_uart_mvp_validation_session.csv`](../../04_PC_Serial_Control/logs/2026-07-09_uart_mvp_validation_session.csv)

Key extracted sequence:

```text
PING,seq=1 -> PONG,seq=1
CMD,seq=2 -> ERR,code=NOT_ARMED
ARM,seq=3 -> ACK,type=ARM
CMD,seq=20,vx_mmps=50,w_mradps=0,timeout_ms=500 -> ACK,type=CMD
TEL,last_seq=20,vx_mmps=50 -> TEL,last_seq=20,vx_mmps=0
CMD,seq=25,vx_mmps=9999 -> ERR,code=OUT_OF_RANGE
DISARM,seq=26 -> ACK,type=DISARM
```

## Timeout Detail

CSV에서 `seq=20` 기준 command timeout이 다음처럼 관찰됐다.

```text
2026-07-09T08:52:06.939Z  TEL,last_seq=20,vx_mmps=50
2026-07-09T08:52:07.039Z  TEL,last_seq=20,vx_mmps=50
2026-07-09T08:52:07.139Z  TEL,last_seq=20,vx_mmps=50
2026-07-09T08:52:07.239Z  TEL,last_seq=20,vx_mmps=50
2026-07-09T08:52:07.338Z  TEL,last_seq=20,vx_mmps=50
2026-07-09T08:52:07.438Z  TEL,last_seq=20,vx_mmps=0
```

`timeout_ms=500` command 이후 약 500ms 지점에서 `vx_mmps=0`으로 전환된다.

## Result

| Area | Result |
| --- | --- |
| UART connection | PASS |
| Periodic telemetry | PASS |
| PING/PONG | PASS |
| ACK response | PASS |
| ERR response | PASS |
| Safety gate before ARM | PASS |
| ARMED valid CMD | PASS |
| Timeout output zero | PASS |
| Range validation | PASS |
| DISARM safe return | PASS |

## Issues / Notes

- `LAST CODE` field는 마지막 error code를 유지한다. 그래서 정상 ACK 이후에도 이전 error가 화면에 남아 보일 수 있다. 현재 검증에서는 `LAST TX`, `LAST ACK`, `LAST ERR`, `LAST RX`, Raw Log를 함께 보고 판단한다.
- `timeout_ms=3000`은 dashboard 입력은 가능하지만 firmware rule상 허용 범위 밖이다. STM32는 이를 `TIMEOUT_OUT_OF_RANGE`로 거부한다.
- 이번 테스트는 실제 motor output을 검증하지 않았다. 다음 단계에서 MDD10A logic input, PWM/DIR output, motor no-load test로 이어가야 한다.

## Next Actions

1. MDD10A visual and multimeter inspection 수행
2. buck converter calibration 기록
3. MDD10A logic input test 수행
4. STM32 PWM/DIR output과 UART CMD를 연결
5. encoder feedback 추가 후 telemetry에 `left_cps`, `right_cps` 반영


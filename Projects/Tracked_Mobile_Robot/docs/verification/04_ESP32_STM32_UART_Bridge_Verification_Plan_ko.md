# ESP32-STM32 UART Bridge Verification Plan

## 목적

이 문서는 ESP32-S3 DevKitC가 STM32 UART MVP의 command source / telemetry relay로 동작하는지 검증하기 위한 계획이다.

이 검증은 PC-first UART MVP 다음 단계다.

```text
PC-first UART MVP:
PC Web Serial Dashboard
<-> STM32 USART2

ESP32 bridge MVP:
PC Serial Monitor
<-> ESP32 USB Serial
<-> ESP32 UART
<-> STM32 USART1
```

## 검증 범위

검증 포함:

- ESP32 UART loopback
- ESP32 -> STM32 `PING/PONG`
- ESP32 -> STM32 `ARM/CMD/DISARM`
- STM32 -> ESP32 `ACK/ERR/TEL`
- ESP32 USB Serial logging
- command timeout 이후 telemetry zero 확인

검증 제외:

- Wi-Fi dashboard
- WebSocket bridge
- MDD10A motor output
- actual drivetrain motion
- encoder feedback

## Assumptions

- STM32 UART MVP rule은 2026-07-09 PC-first 검증에서 PASS했다.
- STM32는 ESP32 bridge용 UART로 USART1 PA9/PA10을 사용한다.
- ESP32와 STM32는 3.3 V UART logic을 사용한다.
- ESP32와 STM32는 common GND를 공유한다.
- STM32가 최종 safety authority다.

## Requirements

### REQ-BRIDGE-001: ESP32 UART loopback

ESP32는 외부 UART TX/RX loopback에서 line-based frame을 송수신할 수 있어야 한다.

Acceptance criteria:

- ESP32 TX: `PING,seq=1`
- ESP32 RX: `PING,seq=1`
- PC USB Serial Monitor에 TX/RX log가 출력된다.

### REQ-BRIDGE-002: ESP32 to STM32 link health check

ESP32는 STM32로 `PING`을 보내고 `PONG`을 수신해야 한다.

Acceptance criteria:

- ESP32 TX: `PING,seq=1`
- ESP32 RX: `PONG,seq=1,t_ms=...`

### REQ-BRIDGE-003: command sequence forwarding

ESP32는 STM32 UART MVP command frame을 생성하거나 forwarding할 수 있어야 한다.

Acceptance criteria:

- `CMD` before `ARM` -> `ERR,code=NOT_ARMED`
- `ARM` -> `ACK,type=ARM`
- valid `CMD` -> `ACK,type=CMD`
- invalid range `CMD` -> `ERR,code=OUT_OF_RANGE`
- `DISARM` -> `ACK,type=DISARM`

### REQ-BRIDGE-004: telemetry relay

ESP32는 STM32가 송신하는 `TEL` frame을 PC USB Serial Monitor로 relay해야 한다.

Acceptance criteria:

- `TEL,state=DISARMED` 관찰
- `TEL,state=ARMED` 관찰
- valid `CMD` 이후 `TEL,last_seq=N,vx_mmps=50` 관찰
- timeout 이후 `TEL,last_seq=N,vx_mmps=0` 관찰

### REQ-BRIDGE-005: STM32 safety authority preserved

ESP32가 command source가 되어도 STM32가 safety gate와 timeout을 계속 소유해야 한다.

Acceptance criteria:

- ESP32는 `CMD`를 요청할 뿐 PWM/DIR output을 직접 소유하지 않는다.
- `DISARMED` 상태의 `CMD`는 STM32가 거부한다.
- out-of-range command는 STM32가 거부한다.
- command timeout output zero는 STM32 telemetry에서 확인된다.

## Test Matrix

| Test ID | Requirement | Procedure | Expected | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| T-BRIDGE-001 | REQ-BRIDGE-001 | ESP32 UART TX/RX loopback 연결 후 `PING,seq=1` 송신 | RX에서 동일 frame 수신 | `2026-07-14_09_esp32_uart1_loopback_ping_rx.png` | PASS |
| T-BRIDGE-002 | REQ-BRIDGE-002 | ESP32 UART와 STM32 USART1 연결 후 `PING,seq=1` 송신 | `PONG,seq=1` 수신 | `2026-07-14_11_esp32_stm32_uart_ping_pong_tel_success.png` | PASS |
| T-BRIDGE-003 | REQ-BRIDGE-003 | ESP32 scripted command sequence 실행 | `NOT_ARMED`, `ACK`, `OUT_OF_RANGE`, `DISARM` 확인 | 2026-07-20 screenshot / raw log | PASS |
| T-BRIDGE-004 | REQ-BRIDGE-004 | ESP32가 STM32 `TEL` frame relay 및 세부 field 구조화 | `DISARMED`, `ARMED`, valid CMD, timeout-zero `TEL` 확인 | 2026-07-18 / 2026-07-20 screenshots | PASS |
| T-BRIDGE-005 | REQ-BRIDGE-005 | valid `CMD` 1회 송신 후 추가 CMD 중단 | timeout 후 `vx_mmps=0`, `w_mradps=0` | 2026-07-20 screenshot / raw log | PASS |

`T-BRIDGE-003`부터 `T-BRIDGE-005`까지는 2026-07-20 실제 ESP32-S3와 STM32 USART1 연결에서 검증했다. 첫 실행은 STM32가 이전 세션의 `ARMED` 상태였기 때문에 precondition이 맞지 않아 재시험했고, 최종 실행은 `DISARMED` 상태에서 시작해 전체 acceptance criteria를 만족했다.

## 2026-07-20 Execution Snapshot

확인 완료:

- `CMD,seq=2` before ARM -> `ERR,code=NOT_ARMED`
- `ARM,seq=3` -> `ACK,type=ARM`, 이후 `TEL,state=ARMED`
- valid `CMD,seq=4` -> `ACK,type=CMD`, `TEL,vx_mmps=50`
- 약 300 ms command timeout 이후 `TEL,vx_mmps=0,w_mradps=0`
- invalid `CMD,seq=5` -> `ERR,code=OUT_OF_RANGE`, `last_seq=4` 유지
- `DISARM,seq=6` -> `ACK,type=DISARM`, 이후 `TEL,state=DISARMED`

Evidence:

- `../../assets/screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png`
- `../../assets/logs/esp32_uart_bridge/2026-07-20_scripted_safety_sequence_pass.txt`

판정: ESP32-STM32 board-only UART bridge MVP PASS.

## 2026-07-18 Execution Snapshot

확인 완료:

- ESP32 structured `TEL` parser build / flash / monitor
- `state=DISARMED`, `vx=0`, `w=0` 반복 출력
- ESP32 `PING seq`에 따른 STM32 `PONG`과 `TEL last_seq` 갱신
- `tel_count` 연속 증가 및 parse error 미발생

Evidence:

- `../../assets/screenshots/esp32_uart_bridge/2026-07-18_13_esp32_structured_tel_parser_success.png`

다음 검증:

- `T-BRIDGE-003` scripted command sequence
- `T-BRIDGE-004`의 `ARMED` 및 valid `CMD` telemetry 항목
- `T-BRIDGE-005` timeout-zero telemetry

## 2026-07-14 Execution Snapshot

확인 완료:

- ESP32 UART1: `GPIO17 TX`, `GPIO18 RX`, `115200 8N1`
- STM32 USART1: `PA9 TX`, `PA10 RX`, `115200 8N1`
- wiring: ESP32 TX -> STM32 RX, ESP32 RX <- STM32 TX, common GND
- loopback: `TX PING`과 동일한 `RX PING`
- integration: ESP32 `PING` -> STM32 `PONG`
- relay: STM32 `TEL` -> ESP32 USB monitor
- parser: ESP32가 `TEL`과 `PONG`을 구분하고 counter 증가

아직 확인하지 않음:

- ESP32 scripted `CMD before ARM`
- `ARM`, valid `CMD`, invalid range `CMD`, `DISARM`
- `ARMED` telemetry와 valid command 값 반영
- command 중단 후 timeout-zero telemetry

관련 evidence는 `../../assets/screenshots/esp32_uart_bridge/README.md`의 09-12 항목을 참조한다.

## Suggested Test Sequence

```text
1. ESP32 UART loopback - PASS
2. STM32 USART1 firmware bring-up - PASS
3. ESP32 -> STM32 PING/PONG - PASS
4. ESP32 telemetry relay in DISARMED state - PASS
5. ESP32 detailed TEL parser - PASS
6. ESP32 scripted command sequence - PASS
7. ARMED/CMD/timeout telemetry 확인 - PASS
8. evidence 저장 및 verification matrix 최종 업데이트 - PASS
```

## Evidence Naming

추천 스크린샷:

```text
assets/screenshots/esp32_uart_bridge/YYYY-MM-DD_01_esp32_uart_loopback.png
assets/screenshots/esp32_uart_bridge/YYYY-MM-DD_02_esp32_stm32_ping_pong.png
assets/screenshots/esp32_uart_bridge/YYYY-MM-DD_03_esp32_cmd_before_arm_not_armed.png
assets/screenshots/esp32_uart_bridge/YYYY-MM-DD_04_esp32_arm_cmd_ack.png
assets/screenshots/esp32_uart_bridge/YYYY-MM-DD_05_esp32_timeout_zero_telemetry.png
assets/screenshots/esp32_uart_bridge/YYYY-MM-DD_06_esp32_disarm_state_disarmed.png
```

추천 로그:

```text
assets/logs/esp32_uart_bridge/YYYY-MM-DD_scripted_safety_sequence_pass.txt
```

## Pass Criteria

ESP32-STM32 UART bridge MVP는 다음을 만족하면 PASS로 본다.

- ESP32 loopback PASS
- ESP32가 STM32 `PONG` 수신
- ESP32 command sequence에서 기대 `ACK/ERR` 수신
- STM32 telemetry가 ESP32를 통해 PC에 표시
- command timeout 이후 zero telemetry 확인
- STM32 safety authority 원칙 유지

## Follow-up

이 검증이 PASS되면 다음 확장을 고려한다.

1. MDD10A PWM/DIR logic input test
2. STM32 UART command state를 PWM/DIR output path와 연결
3. encoder signal voltage 및 count validation
4. low-duty motor no-load test
5. ESP32 Wi-Fi/WebSocket relay는 drivetrain baseline 이후 선택적으로 확장

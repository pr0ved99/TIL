# 2026-08-04 UART Runtime And Active DISARM Handoff

This handoff supersedes
[`2026-08-03_uart_response_gated_startup_implementation_handoff.md`](2026-08-03_uart_response_gated_startup_implementation_handoff.md)
as the current UART/motor-output continuation source.

## 현재 목표

현재 safe-restored source로 만든 images를 양쪽 board에 reflash/run하고 ARM/CMD 0
회귀를 보존한 뒤 required wrong ACK type과 Gate C의 ESP-response/STM32-command
parser recovery를 닫는다. Source restore, contract와 isolated clean build는 완료됐다.

```text
Gate A runtime behavior: PASS
Gate B bounded failure: PASS
Gate B stale-sequence rejection/reset-new-startup recovery: PASS behavior;
post-failure linkage pending
Gate C controlled normal sequence: PASS
Gate C ESP-response/STM32-command parser recovery: NOT TESTED
Active DISARM MCU-pin baseline: PASS, 23.50 us
Current release: PARTIAL
Current source/static/build restore: PASS
Safe-image board reflash/run: PENDING
```

## 완료된 Runtime Evidence

### Gate A

- `DISARM,seq=S`와 exact `ACK,seq=S,type=DISARM`
- `PING,seq=S+1`과 exact `PONG,seq=S+1`
- 두 matching response 뒤에만 READY
- ARM/CMD TX 0회
- telemetry DISARMED/zero

### Gate B

- DISARM ACK loss: same request 3회, 500 ms 간격, then FAILED
- PONG loss: DISARM ACK 뒤 same PING 3회, then FAILED
- FAILED 실행에서 READY/ARM/CMD 없음
- controlled reset 뒤 새 `S/S+1` startup recovery
- stale ACK seq와 stale PONG seq 무시 뒤 exact response만 통과
- matching seq + wrong ACK type은 별도 runtime vector가 없어 open

원본 파일명 `gate_c1/c2`는 바꾸지 않는다. 두 파일은 의미상 Gate B의
stale-response rejection evidence다.

### Gate C normal sequence and active DISARM

READY 이후 controlled `1U` script에서 NOT_ARMED, ARM, valid CMD,
OUT_OF_RANGE, active DISARM을 확인했다. 같은 capture에서 DISARM final LF 수신
완료부터 PB6/PB7 last-active-edge까지 23.50 us였고, PWM은 ACK보다 62.75 us
먼저 멈췄다.

이 결과는 STM32 MCU pin만 검증한다. MDD10A power output, actual motor stop,
mechanical stop, Physical E-stop을 통과시킨 것이 아니다.

## Current Actual Source And Preflight State

2026-08-04 실제 파일 기준:

| Macro/setting | Current safe value |
| --- | ---: |
| ESP `BRIDGE_SCRIPTED_TEST_ENABLED` | `0U` |
| ESP `TEST_STEP_PERIOD_MS` | `1000` |
| STM `UART_MVP_OUTPUT_TEST_ENABLED` | `0U` |
| STM stale ACK injection | `0U` |
| STM stale PONG injection | `0U` |
| STM suppress PONG injection | `0U` |
| STM button output/fault hooks | `0U` |

현재 firmware contract suite는 `15/15 PASS`다. Isolated clean STM32/ESP32 build도
run `20260804043010-26408-7918`에서 모두 PASS했다. 이 결과는 source/configuration과
build artifact까지만 검증하며, restored images가 board에 실행 중이라는 증거는 아니다.

## 완료된 단계: Safe Source/Static/Build Restore

- ESP `BRIDGE_SCRIPTED_TEST_ENABLED=0U`
- ESP `TEST_STEP_PERIOD_MS=1000`
- STM `UART_MVP_OUTPUT_TEST_ENABLED=0U`
- firmware contract `15/15 PASS`
- isolated clean STM32/ESP32 build `PASS` (`20260804043010-26408-7918`)

Board에는 이전 controlled-test image가 남아 있을 수 있다. Safe-image board
reflash/run과 ARM/CMD 0 raw evidence 전까지 board 상태는 복구 완료로 판정하지 않는다.

## Safe Build/Flash Regression

Source restore와 필요한 STM32/ESP32 isolated clean build는 PASS했다. Build PASS는
board runtime 증거가 아니므로, 이어서 사용자가 safe images를 flash/run하고 다음을
새 raw log로 확인한다.

- matching DISARM ACK와 PONG 뒤 READY
- READY 이전 및 이후 scripted ARM/CMD TX 0회
- telemetry DISARMED/zero
- 반복 reset, 과열, 냄새, USB 불안정 없음

Flash transcript와 binary hash를 함께 보존하면 현재 raw evidence의 image-identity
gap을 줄일 수 있다.

## 다음 Open Gate: T-BRIDGE-007 completion과 Gate C parser recovery

Safe restore와 safe-image 회귀 뒤, motor power가 없는 controlled 환경에서 실행한다.

먼저 matching seq + wrong ACK type을 주입하고 DISARM ACK wait state가 열리지 않는지
확인해 T-BRIDGE-007의 required gap을 닫는다.

### Gate C1: ESP32 startup-response parser

ESP32가 DISARM ACK 또는 PONG을 기다리는 동안 duplicate required field, numeric
overflow, trailing comma, invalid terminator, partial frame name, embedded control/overlong
line 같은 명확한 invalid response를 주입한 뒤 현재 wait state에 맞는 exact response를
보낸다. Unknown extra field는 이 parser에서 허용되므로 reject vector로 사용하지 않는다.

PASS 기준:

- invalid response가 ACK/PONG latch나 READY를 만들지 않음
- 현재 request와 일치하는 exact ACK/PONG에서만 다음 state로 진행
- parser가 복구되고 unrecovered overflow/desync가 없음
- 별도의 ARM 또는 유효한 motion CMD 송신 없음

### Gate C2: STM32 command parser

```text
DISARM,seq=100
PING,seq=101,extra=1
CMD field order violation with seq=102
BAD,seq=103
PING,seq=104
```

ESP32의 startup **response parser**는 forward compatibility를 위해 unknown extra
field를 허용하지만, 이 C2가 주입하는 대상은 STM32 **command parser**다. Current
STM32 parser는 non-CMD extra data를 거부하고 CMD field order를 강제하므로
`PING,seq=101,extra=1`과 field-order-invalid CMD는 reject vector가 맞다. 실행 전에도
실제 parser source와 주입 방향을 다시 확인하고 duplicate field, overflow, invalid
terminator, embedded control/overlong line vector를 필요에 따라 추가한다.

C2 PASS 기준:

- invalid/malformed command가 실행되지 않음
- telemetry가 DISARMED/zero 유지
- final valid PING에 matching PONG
- unrecovered RX overflow/desync 없음
- 별도의 ARM 또는 유효한 motion CMD 송신 없음; 주입한 malformed CMD는 실행이나
  출력 변화를 만들지 않음

## Evidence

- [Response-gated startup report](../verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md)
- [Active DISARM latency report](../verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)
- [2026-08-04 progress](../progress/2026-08-04_progress.md)
- [UART raw logs](../../assets/logs/esp32_uart_bridge/README.md)
- [Logic-analyzer capture index](../../assets/captures/logic_analyzer/README.md)

## Evidence Boundary Pending Operator Confirmation

Gate A/B와 active DISARM raw files에는 LiPo/MDD10A/motor power 분리, UART 변경 시
양쪽 보드 전원 OFF, analyzer logic-pin-only 연결 조건이 text metadata로 들어 있지
않다. 작업자가 확인하기 전까지 해당 시험 조건은 `operator confirmation pending`이다.

## 다음 안전 시험 순서

Completed: safe source restore, contract `15/15`, isolated clean dual build.

1. Safe images flash/run and no-ARM/CMD evidence
2. Required matching-seq/wrong-ACK-type rejection
3. Gate C ESP-response and STM32-command parser recovery
4. Final safe restore regression if another controlled hook was used
5. Command-timeout shutdown latency
6. Software-fault shutdown latency/latch
7. External-reset-marker boot no-output
8. Board power/back-power and Physical E-stop gates
9. Only then lifted/no-load actual motor test

## 절대 유지할 규칙

- STM32가 parser, command timeout, motor output과 최종 safety authority다.
- ESP32는 command source/relay/logger이며 elapsed time만으로 peer readiness를
  가정하지 않는다.
- UART Gate에서 LiPo, MDD10A B+/B- 또는 actual motor power를 연결하지 않는다.
- 양쪽 board를 USB로 전원 공급할 때 5 V/VBUS/VIN rail을 서로 연결하지 않는다.
- Static/build PASS를 board runtime 또는 electrical PASS로 확대하지 않는다.
- MCU-pin capture를 driver/motor/E-stop PASS로 확대하지 않는다.
- 원본 `.txt`, `.sr`, `.pvs`, `.png` evidence를 편집하거나 덮어쓰지 않는다.
- 사용자가 요청하기 전에는 commit/push하지 않는다.

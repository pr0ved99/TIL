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
- startup session을 응답으로 확인한 뒤에만 scripted `ARM/CMD` 허용
- startup 응답 유실·잘못된 응답에서 bounded retry 후 fail-closed 정지
- malformed frame 거부 후 정상 frame으로 복구

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

### REQ-BRIDGE-006: response-gated startup

ESP32는 고정 시간만 기다린 뒤 STM32가 준비됐다고 추측하지 않는다. 다음 단계의
응답을 정확히 확인한 경우에만 startup을 진행해야 한다.

Acceptance criteria:

- 부팅 후 `500 ms` settle, newline boundary sync, `100 ms` 대기와 RX buffer/line-state reset을 수행한다.
- 부팅마다 시작 sequence `S`를 새로 생성하고 `DISARM,seq=S`를 송신한 뒤 정확한 `ACK,seq=S,type=DISARM`만 수락한다.
- 이어서 `PING,seq=S+1`을 송신하고 정확한 `PONG,seq=S+1`만 수락한다.
- 각 응답 대기는 `500 ms`, 각 요청은 최대 3회 시도한다.
- ACK/PONG은 해당 응답 wait state에서만 latch하며, 이른 응답·이전 부팅의 늦은 응답·일치하지 않는 `seq`/`type` 또는 malformed field는 성공으로 인정하지 않는다.
- UART TX 또는 RX flush/reset 실패는 성공으로 넘기지 않고 `FAILED`로 닫힌다.
- 두 단계가 모두 성공해야 `READY`가 되며, 실패하면 `FAILED`에 머문다.
- `READY` 전과 `FAILED`에서는 scripted `ARM/CMD`를 송신하지 않는다.

### REQ-BRIDGE-007: ESP32 startup-response exact-field parsing and recovery

ESP32 startup-response parser는 쉼표로 구분된 정확한 field 이름과 값 경계를
확인해야 한다.

Acceptance criteria:

- `badseq=1`, `seq=1x`, `badtype=DISARM` 같은 부분 문자열과 `PONGX,` 같은 부분 frame 이름을 정상으로 오인하지 않는다.
- required field 중복, 숫자 overflow, trailing comma와 유효하지 않은 종결 문자를 거부한다.
- unknown extra field는 forward compatibility를 위해 허용하되 required field는 정확히 한 번 존재해야 한다.
- overlong line, embedded CR/control/NUL/DEL이 나타난 line은 LF까지 전부 폐기한다.
- malformed frame이나 알 수 없는 response frame을 startup 성공으로 처리하지 않는다.
- 거부 뒤 현재 wait state에 맞는 exact `ACK` 또는 `PONG`을 수신하면 startup 응답
  경로가 복구된다.

### REQ-BRIDGE-008: STM32 command-parser fail-closed recovery

ESP32 response parser와 별도로, ESP32가 STM32 command parser 쪽으로 보내는
malformed/unknown command frame이 동작으로 실행되지 않고 다음 정상 frame에서 수신
경로가 복구돼야 한다.

Acceptance criteria:

- extra data가 붙은 non-CMD frame, field-order-invalid/duplicate/overflow CMD와 unknown
  frame을 STM32가 거부한다.
- 거부된 frame은 motion output을 만들지 않고 telemetry는 `DISARMED/zero`를 유지한다.
- overlong line이나 embedded control/invalid terminator 뒤에도 다음 line boundary에서
  복구한다.
- 마지막 valid `PING`에는 matching `PONG`을 반환한다.

## Test Matrix

| Test ID | Requirement | Procedure | Expected | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| T-BRIDGE-001 | REQ-BRIDGE-001 | ESP32 UART TX/RX loopback 연결 후 `PING,seq=1` 송신 | RX에서 동일 frame 수신 | `2026-07-14_09_esp32_uart1_loopback_ping_rx.png` | PASS |
| T-BRIDGE-002 | REQ-BRIDGE-002 | ESP32 UART와 STM32 USART1 연결 후 `PING,seq=1` 송신 | `PONG,seq=1` 수신 | `2026-07-14_11_esp32_stm32_uart_ping_pong_tel_success.png` | PASS |
| T-BRIDGE-003 | REQ-BRIDGE-003 | ESP32 scripted command sequence 실행 | `NOT_ARMED`, `ACK`, `OUT_OF_RANGE`, `DISARM` 확인 | 2026-07-20 screenshot / raw log | PASS |
| T-BRIDGE-004 | REQ-BRIDGE-004 | ESP32가 STM32 `TEL` frame relay 및 세부 field 구조화 | `DISARMED`, `ARMED`, valid CMD, timeout-zero `TEL` 확인 | 2026-07-18 / 2026-07-20 screenshots | PASS |
| T-BRIDGE-005 | REQ-BRIDGE-005 | valid `CMD` 1회 송신 후 추가 CMD 중단 | timeout 후 `vx_mmps=0`, `w_mradps=0` | 2026-07-20 screenshot / raw log | PASS |
| T-BRIDGE-006 | REQ-BRIDGE-006 | Motor power OFF, safe macro `0U`에서 ESP32와 STM32를 cold start | matching DISARM ACK와 PONG 뒤 READY, ARM/CMD 없음 | [Gate A report](09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md), [current safe log](../../assets/logs/esp32_uart_bridge/2026-08-12_post_t_bridge_008b_safe_uart_runtime_regression_pass.txt), [current report](15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md) | PARTIAL — current all-hooks-`0U`, contract `15/15`, exact startup과 post-READY TEL 123/123 observed UART behavior PASS; external cold-start marker, exact source-to-board linkage와 log-embedded physical provenance pending |
| T-BRIDGE-007 | REQ-BRIDGE-006 | DISARM ACK 또는 PONG 단절·wrong seq/type 주입 | loss는 단계별 최대 3회 뒤 FAILED; mismatch는 무시·재시도하고 exact response만 통과; ARM/CMD 없음 | [Loss/stale/reset report](09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md), [wrong-type raw log](../../assets/logs/esp32_uart_bridge/2026-08-04_response_gated_startup_wrong_disarm_ack_type_rejection_pass.txt) | PASS — required UART runtime behavior; binary identity와 physical setup provenance pending |
| T-BRIDGE-008A | REQ-BRIDGE-007 | ESP32가 ACK/PONG을 기다릴 때 malformed/unknown response 뒤 exact response 주입 | invalid response는 gate를 열지 않고 exact response에서 recovery | [2026-08-06~12 evidence and report](15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md) | PASS — duplicate required `seq`, trailing comma, uint32 overflow, partial frame name, embedded CR, control byte와 overlong-line required runtime vectors; exact artifact/setup provenance는 별도 pending |
| T-BRIDGE-008B | REQ-BRIDGE-008 | STM32에 malformed PING/CMD/unknown frame 뒤 valid PING 주입 | motion 실행 없는 fail-closed 거부 후 PONG recovery | [008B raw log](../../assets/logs/esp32_uart_bridge/2026-08-12_t_bridge_008b_stm32_malformed_command_rejection_recovery_pass.txt), [report 15](15_UART_Gate_C_Invalid_Control_And_STM32_Command_Recovery_Test_Report_2026-08-12_ko.md) | PASS — 8/8 malformed/unknown frame ERR, TEL 200/200 DISARMED/zero, final `PING,seq=9009` matching PONG recovery |

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

이 판정은 2026-07-20 baseline에 한정한다. 이후 strict parser와 startup logic이 변경됐으므로
현재 release는 아래 2026-08-03 gate를 닫기 전까지 `PARTIAL`이다.

## 2026-08-03 Response-Gated Startup Implementation And Runtime Checkpoint

소스에는 `SETTLE -> SYNC_WAIT -> WAIT_DISARM_ACK -> WAIT_PONG -> READY/FAILED`
상태 머신, 부팅별 sequence `S/S+1`, state-scoped response latch, TX/flush fail-closed와
corrupted-line discard가 구현됐다. 정적 firmware contract test `15/15`와
ESP32-S3 build도 통과했으며 app image는 `0x2b210` bytes, smallest app partition은
`83% free`였다.

15개 test는 host parser vector와 source/configuration contract 검사를 함께 포함하며 새
FSM/parser의 모든 분기를 실행하는 host test는 아니다. 이 source/build checkpoint와 별도로
실제 board raw log를 확보했다.

- Gate A: exact DISARM ACK와 PONG 뒤 READY, ARM/CMD 없음 — PASS
- Gate B1: DISARM ACK 누락, 동일 request 최대 3회 뒤 FAILED — PASS
- Gate B2: PONG 누락, 동일 request 최대 3회 뒤 FAILED — PASS
- stale ACK/PONG sequence: 무시 뒤 exact response만 통과 — PASS
- controlled reset: 새 S/S+1 startup recovery — PASS
- matching-seq wrong ACK type: `type=ARM` 무시, 정확히 500 ms 뒤 동일 DISARM seq
  재시도, exact DISARM ACK와 PONG 뒤에만 READY — PASS
- wrong-type run safety: TEL 97/97 `DISARMED/zero`, ARM/CMD TX 0 — PASS
- ESP32 duplicate-required-`seq` ACK reject 뒤 same-seq retry와 exact response recovery — PASS
- ESP32 trailing-comma ACK reject 뒤 same-seq retry와 exact response recovery — PASS
- ESP32 required-`seq` uint32-overflow ACK reject 뒤 same-seq retry와 exact response recovery — PASS
- ESP32 partial frame name response rejection/recovery — PASS
- ESP32 embedded CR/control byte와 overlong-line/RX-line-overflow response rejection/recovery — PASS
- STM32 malformed/unknown command 8-vector reject 뒤 valid PING/PONG recovery — PASS
- Final all-hooks-`0U` exact startup, ARM/CMD/error 0, post-READY TEL 123/123 safe — PASS

Raw log는 실제 flash hash와 LiPo/MDD10A/motor power 분리 상태를 자체 기록하지 않는다.
따라서 T-BRIDGE-006의 visible runtime transaction은 PASS지만 cold-start marker와
physical/macro provenance는 작업자 확인 대기이므로 Test ID 전체는 PARTIAL이다.
T-BRIDGE-007 required UART runtime behavior는 loss, stale seq, reset recovery와
matching-seq/wrong-type rejection까지 PASS했다. 다만 binary identity와 physical setup
provenance는 별도 pending이다. T-BRIDGE-008A와 T-BRIDGE-008B required runtime vectors는
2026-08-12까지 PASS했다. Gate C runtime scope와 별도로 exact runtime-to-artifact identity,
external cold-start marker와 log-embedded physical setup provenance는 pending이다.

2026-08-04 earlier safe-source checkpoint의 ESP script `0U/1000 ms`, STM32 UART
output hook `0U`, contract `15/15`와 isolated clean STM32/ESP32 build run
`20260804043010-26408-7918`은 PASS다. 이어진 safe-image runtime도 exact
ACK/PONG/READY, READY 뒤 약 11.24 s, TEL 118/118 `DISARMED/zero/error 0`, ARM/CMD
TX 0으로 behavior PASS했다. 로그 자체는 flash identity와 물리 무전원 setup을 증명하지
않는다.

2026-08-06에는 먼저 wrong-ACK hook을 `0U`로 복구해 ESP/STM의 모든 controlled hook이
`0U`다. Current source의 contract `15/15`와 STM32CubeIDE build가 PASS했다. 이와
별도로 final board log에서 observed UART runtime behavior도 PASS했다. Log는 exact
ACK/PONG/READY, READY 후 11.35 s, TEL 120/120
`DISARMED/zero/error 0`, ARM/CMD와 parser/startup error 0이다. Exact ELF-to-board
linkage와 physical setup provenance, 두 parser recovery가 남아 있던 pre-008A historical
checkpoint다.

같은 날 T-BRIDGE-008A의 첫 malformed-response vector를 실행했다. First DISARM
`seq=1313693021`에 duplicate required `seq`를 가진 ACK를 주입하자 ESP32가 parser error로
1회 거부했고, READY/PING으로 조기 진행하지 않았다. 정확히 500 ms 뒤 같은 DISARM seq를
재시도해 첫 exact ACK를 `ack_count=1`로 수락하고 `PONG seq=1313693022` 뒤에만 READY가
열렸다. TEL 150/150은 `DISARMED/zero/error 0`이고 ARM/CMD, attempt 3와 startup failure는
0건이다.

Controlled build는 `0 errors / 0 warnings`, ELF SHA-256
`9565A1405FF97BE75BC1D30F87DEBD1CE32ED05D8E16525D2205231AD74CCA61`였고 flash verify가
완료됐다. 시험 뒤 모든 hook을 `0U`로 복구해 contract `15/15`, safe build `0 errors /
0 warnings`, ELF SHA-256 `25885322BD28B19456498A37C14B87D039984A96F2E2EA30CC1764A36E086A2A`,
safe flash verify를 확인했다. 마지막 safe log는 retry/parser error 없이 exact startup,
READY 후 14.42 s, TEL 150/150 safe와 ARM/CMD 0을 보인다. 따라서 duplicate-required-`seq`
subvector는 PASS지만 나머지 response vectors와 T-BRIDGE-008B가 남아 release는 `PARTIAL`이다.

2026-08-06~07 trailing-comma vector에서는 first DISARM `seq=951827278`의 otherwise-valid
ACK 끝 comma를 ESP32가 `RX malformed field list`로 1회 거부했다. 정확히 500 ms 뒤 같은
DISARM seq를 재시도했고 first exact ACK `ack_count=1`, `PONG seq=951827279` 뒤에만 READY가
열렸다. TEL 150/150은 safe이고 ARM/CMD, attempt 3와 startup failure는 0건이다. Controlled
build는 `0 errors / 0 warnings`, ELF SHA-256
`5791C9B1E5A8F2ED942B8A8A0BDD8599C2A775EDB5D59022E60CE900C52B406E`, flash verify PASS다.
시험 뒤 모든 hook `0U`, contract `15/15`, controlled string 부재와 safe flash verify를
확인했다. 당시 post-trailing safe ELF SHA-256은
`3526206C7E2043634029B15B7D41F9C80B136904FCA72FB46D8CA24F4119DEE4`이고, safe runtime은
warning/retry/parser error 없이 READY 후 15.51 s, TEL 160/160 safe, ARM/CMD 0이다. 이후
post-Clean full build가 31개 object 전체를 재컴파일·링크해 `0 errors / 0 warnings`였고
object/ELF/map/list hashes를 byte-identical하게 재현했다.

2026-08-07 required-`seq` uint32-overflow vector에서는 first DISARM `seq=545713623`에 대해
`ACK,seq=4294967296,type=DISARM,t_ms=567`을 주입했다. ESP32는 이를 `RX ACK parse error`로
정확히 1회 거부했고, 500 ms 뒤 같은 DISARM seq를 재시도해 first exact ACK
`ack_count=1`, `PONG seq=545713624` 뒤에만 READY가 열렸다. READY 뒤 13.90 s 동안 완전한
TEL 140/140은 모두 `DISARMED/zero/error 0`이었고 ARM/CMD, attempt 3와 startup failure는
0건이다. Controlled build는 `0 errors / 0 warnings`, ELF SHA-256
`747F32E3BDFBF0D4130E2F136145806AE88FF4F94BBC8948C7FFB554BE0A3701`였고 flash verify가
PASS했다. 시험 뒤 모든 hook을 `0U`로 복구해 contract `15/15`를 확인했고,
`uart_mvp_protocol.c`를 다시 컴파일하고 ELF를 링크한 incremental build도 `0 errors /
0 warnings`였다. Current safe ELF SHA-256은
`244DD5D31192591AA35866D7529FF7596D3A56CE87E0596F34BFFDBB459E5F6B`이며 overflow
controlled string은 object/ELF/map/list에 없다. Safe flash verify 뒤 exact startup과 READY
후 14.43 s, 완전한 post-READY TEL 145/145 safe, warning/retry/parser error와 ARM/CMD/failure
0으로 회귀 PASS했다.

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
9. response-gated startup board run - PASS behavior / provenance confirmation pending
10. response-loss bounded retry, stale-seq rejection, reset recovery와 wrong ACK type - PASS behavior / provenance pending
11. ESP malformed-response recovery - PASS: planned required runtime vectors
12. STM command parser malformed reject/recovery - PASS: 8/8 reject + final matching PONG
13. post-Gate-C all-hooks-0U·15/15 + final safe exact startup + post-READY TEL 123/123 PASS / exact linkage·physical setup provenance PENDING
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
assets/logs/esp32_uart_bridge/YYYY-MM-DD_response_gated_startup_safe_macro0_pass.txt
assets/logs/esp32_uart_bridge/YYYY-MM-DD_startup_wrong_or_missing_response_fail_closed_pass.txt
assets/logs/esp32_uart_bridge/YYYY-MM-DD_malformed_frame_recovery_pass.txt
```

2026-08-04 실제 보존 파일은
`2026-08-04_safe_image_uart_runtime_regression_pass.txt`와
`2026-08-04_response_gated_startup_wrong_disarm_ack_type_rejection_pass.txt`다.

## Pass Criteria

ESP32-STM32 UART bridge MVP는 다음을 만족하면 PASS로 본다.

- ESP32 loopback PASS
- ESP32가 STM32 `PONG` 수신
- ESP32 command sequence에서 기대 `ACK/ERR` 수신
- STM32 telemetry가 ESP32를 통해 PC에 표시
- command timeout 이후 zero telemetry 확인
- STM32 safety authority 원칙 유지

현재 strict-parser release를 PASS로 올리려면 추가로 다음을 만족해야 한다.

- exact DISARM ACK와 PONG을 받은 뒤에만 READY
- 응답 유실·wrong seq/type에서 최대 3회 시도 후 FAILED
- READY 전과 FAILED에서 `ARM/CMD` 무송신
- malformed startup response가 gate를 열지 않고 exact response에서 recovery
- malformed STM32 command의 fail-closed 거부와 정상 PING/PONG recovery
- 시험 종료 후 macro `0U` source/test/build와 safe board flash/run 복구

현재 exact response, bounded loss, stale-sequence, wrong ACK type와 T-BRIDGE-008A planned
malformed-response runtime vectors가 통과했다. T-BRIDGE-008B도 malformed/unknown command
8개를 거부하고 final PING/PONG으로 복구했다. Post-test current all-hooks-`0U`, contract
`15/15`와 별도 board log의 observed safe UART behavior도 PASS했다. Gate C required runtime
scope는 닫혔지만 exact runtime-to-ELF linkage, external cold-start marker와 log-embedded
physical setup provenance가 남아 있으므로 strict-parser release 전체는 아직 `PARTIAL`이다.

## Follow-up

이 검증이 PASS되면 다음 확장을 고려한다.

1. MDD10A PWM/DIR logic input test
2. STM32 UART command state를 PWM/DIR output path와 연결
3. encoder signal voltage 및 count validation
4. low-duty motor no-load test
5. ESP32 Wi-Fi/WebSocket relay는 drivetrain baseline 이후 선택적으로 확장

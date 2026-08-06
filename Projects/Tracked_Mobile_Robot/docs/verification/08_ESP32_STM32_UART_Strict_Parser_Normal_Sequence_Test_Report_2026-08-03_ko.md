# ESP32-STM32 UART Strict-Parser Normal-Sequence Test Report - 2026-08-03

> 이 문서는 fixed-delay controlled run의 역사적 보고서다. 후속 response-gated
> Gate A/B 결과는 [`09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md`](09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md),
> active DISARM pin timing은 [`10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md`](10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)를 따른다.

## 판정

- Controlled normal sequence: `PASS`
- Current strict-parser release gate: `PARTIAL`

이번 시험은 2026-07-31에 관찰한 startup PING 유실과 RX frame-boundary 문제를 다시 확인하기 위한 board-only 회귀시험이다. ESP32 시험 harness에 `500 ms settle -> LF 전송 -> 100 ms 대기 -> PING` preamble을 임시 적용한 뒤, 정상 명령 시퀀스가 current STM32 strict parser에서 끝까지 동작하는지 확인했다.

이 결과는 정상 시퀀스와 단순 frame-boundary preamble이 동작한다는 증거다. 아직 `DISARM ACK`와 `PONG`을 실제로 확인하면서 재시도하는 production-grade startup handshake 및 malformed-frame recovery injection까지 완료한 것은 아니다.

## 시험 조건

| Item | Value |
| --- | --- |
| ESP32 | ESP32-S3 DevKitC, ESP-IDF v6.0.2 |
| STM32 | NUCLEO-F446RE |
| Link | `115200 8-N-1`, common GND |
| ESP TX/RX | GPIO17 TX / GPIO18 RX |
| STM32 RX/TX | PA10 RX / PA9 TX |
| Motor power | MDD10A/Battery power OFF |
| Encoder activity | `left_cps=0`, `right_cps=0` throughout |
| ESP test mode | `BRIDGE_SCRIPTED_TEST_ENABLED=1U` only during capture |
| Startup preamble | 500 ms settle, one LF, 100 ms delay, `PING,seq=1` |

시험 종료 후 source 기본값은 `BRIDGE_SCRIPTED_TEST_ENABLED=0U`로 복구했다. 시험에 사용한 ESP32 board image는 다음 세션의 safe reflash 전까지 controlled-test image일 수 있으므로, overnight에는 두 board USB와 motor/battery power를 분리한다.

위 문장은 이 fixed-delay 시험 종료 당시 상태다. 후속 active-DISARM capture 때 ESP
script `1U/100 ms`, STM32 UART output hook `1U`를 사용했지만 2026-08-04 current
worktree는 `0U/1000 ms`와 STM output hook `0U`로 복구됐다. Contract `15/15`와
isolated clean dual build도 PASS했다. 2026-08-06 follow-up에서 wrong-ACK hook까지
`0U`로 복구하고 current `15/15`와 STM32 build를 PASS했다. 별도 board log의 observed
safe UART behavior도 PASS했다. Exact source-to-board/setup provenance와 reset-marked pin
capture는 pending이다.

## 실제 결과

| Check | Evidence | Result |
| --- | --- | --- |
| Startup PING/PONG | ESP `PING,seq=1` at log time 876 ms, `PONG seq=1` at 916 ms; next TEL `last_seq=1`, `err=0` | PASS |
| CMD before ARM | `CMD,seq=2` -> `ERR,seq=2,type=CMD,code=NOT_ARMED` | PASS |
| ARM | `ARM,seq=3` -> ACK; next TEL `state=ARMED`, `last_seq=3` | PASS |
| Valid CMD | `CMD,seq=4,vx_mmps=50` -> ACK; TEL reports `vx=50` | PASS |
| Timeout zero | STM time 3700~3900 ms samples report `vx=50`; 4000 ms sample reports `vx=0` while remaining ARMED | PASS |
| Range rejection | `CMD,seq=5,vx_mmps=9999` -> `ERR ... OUT_OF_RANGE`; accepted `last_seq` remains 4 | PASS |
| DISARM | `DISARM,seq=6` -> ACK; next TEL `state=DISARMED`, `last_seq=6`, velocity zero | PASS |
| Clean-run unexpected RX error | No `RX_DESYNC`, `RX UNKNOWN` or line overflow occurred during this normal-sequence run | PASS |

The first zero telemetry sample appears within one 100 ms telemetry interval after the configured 300 ms command timeout boundary. This is consistent with timeout-zero behavior; the UART telemetry timestamp does not claim exact shutdown-edge latency.

The final telemetry remained `DISARMED` with `vx=0`, `w=0`, `left_cps=0`, and `right_cps=0`. Final `err=2` is expected: one rejected `NOT_ARMED` command and one rejected `OUT_OF_RANGE` command.

## Evidence

- [Raw ESP32 monitor log](../../assets/logs/esp32_uart_bridge/2026-08-03_strict_parser_normal_sequence_pass.txt)
- [2026-08-03 progress note](../progress/2026-08-03_progress.md)
- [Previous strict-parser/resync observations](../progress/2026-07-31_progress.md)

## 남은 release gate

아래 startup sequence는 이후 ESP32 상태머신에 source 구현되어 정적 contract test와
build를 통과했고, 별도 raw log에서 Gate A exact response와 Gate B bounded failure까지
실행됐다. 이 fixed-delay 보고서 자체를 그 runtime 증거로 재해석하지 않으며 후속
판정은 report 09를 따른다.

```text
UART initialize
-> 500 ms settle
-> newline boundary synchronization
-> RX buffer/line-state reset
-> explicit DISARM,seq=S, where S is generated per boot
-> matching ACK(seq=S,type=DISARM), with bounded retry
-> PING,seq=S+1
-> matching PONG(seq=S+1), with bounded retry
-> READY; scripted safety sequence only when its test macro is enabled
```

Gate A/B와 후속 matching-seq/wrong-ACK-type required runtime behavior는 PASS다.
2026-08-06 current safe source의 all-hooks-`0U`, contract `15/15`와 STM32 build도
PASS했다. 별도 board log의 observed safe UART behavior도 PASS했다. 남은 current
release gate는 ESP response/STM32 command parser의 malformed reject/recovery와 exact
source-to-board/physical setup provenance다.

## 범위 제한

- 이 시험은 UART protocol과 STM32 safety-state behavior를 확인한 board-only 시험이다.
- MDD10A power output, actual motor stop, Physical E-stop 또는 PWM shutdown edge latency를 검증하지 않는다.
- Fixed delay와 one-shot PING만으로 production startup reliability를 보장하지 않는다.

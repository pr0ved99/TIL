# ESP32-STM32 UART Response-Gated Startup Test Report - 2026-08-03

## 판정

```text
Gate A response-gated happy path: PASS — raw runtime behavior
Gate B bounded no-response failure: PASS — DISARM ACK loss and PONG loss
Gate B stale-sequence rejection: PASS — stale ACK seq and stale PONG seq
Gate B controlled reset/new-startup recovery: PASS — post-failure linkage pending
T-BRIDGE-007 required UART runtime vectors: PASS — wrong seq and matching-seq/wrong-type rejection
Gate C controlled normal sequence after READY: PASS
Gate C ESP-response/STM32-command parser recovery: NOT TESTED
Current UART release: PARTIAL
```

이 보고서는 2026-08-03에 저장된 ESP32 monitor 원본 로그와 2026-08-04의
matching-seq/wrong-ACK-type 후속 원본 로그를 읽어
response-gated startup의 실제 제어 흐름을 판정한 결과다. 과거 fixed-delay
정상 시퀀스가 아니라 현재 FSM의 `DISARM/ACK -> PING/PONG -> READY`와
bounded retry를 대상으로 한다.

Gate A와 Gate B의 **UART runtime behavior**는 로그로 확인된다. 다만 원본
로그 자체에는 LiPo·MDD10A B+/B-·실제 모터 전원의 분리 상태, UART 배선 변경
시 양쪽 보드 전원 OFF 여부, flash transcript 또는 실행 binary hash가 포함돼
있지 않다. 따라서 이 물리적 사전 조건과 binary identity는 작업자 확인 전까지
`operator confirmation pending`이며, 로그만으로 전기 안전 조건까지 포함한
완전한 provenance를 주장하지 않는다.

## 대상 설계

```text
SETTLE 500 ms
-> line sync LF
-> SYNC_WAIT 100 ms
-> RX reset
-> DISARM,seq=S
-> matching ACK,seq=S,type=DISARM
-> PING,seq=S+1
-> matching PONG,seq=S+1
-> READY

각 응답 단계:
500 ms timeout
-> 같은 request, 같은 seq로 최초 포함 최대 3회
-> 모두 실패하면 FAILED
```

다음 safety invariant를 판정 기준으로 사용했다.

- Matching DISARM ACK 전에는 PING을 보내지 않는다.
- Matching PONG 전에는 READY에 진입하지 않는다.
- 잘못되거나 stale한 응답은 현재 wait state를 통과시키지 않는다.
- 응답 시도 소진 뒤 `FAILED`로 닫히며 `ARM/CMD`를 송신하지 않는다.
- Controlled reset은 새로운 startup sequence를 시작하며 이전 실패 세션에서
  늦게 도착한 응답만으로 READY가 되지 않는다.

## 시험 인터페이스와 증거 한계

| Item | Value / status |
| --- | --- |
| ESP32 | ESP32-S3 DevKitC |
| STM32 | NUCLEO-F446RE |
| UART | `115200 8-N-1`, ESP GPIO17 TX/GPIO18 RX, STM PA10 RX/PA9 TX, common GND |
| Runtime observer | ESP32 USB monitor raw text |
| Flash transcript / binary hash | 로그에 없음 — 독립 확인 불가 |
| Cold-start / reset marker | 로그에 없음 — 보이는 startup transaction만 판정 가능 |
| LiPo, MDD10A B+/B-, motor power disconnected | operator confirmation pending |
| UART 변경 시 양쪽 board power OFF | operator confirmation pending |
| MDD10A output / actual motor behavior | 이 시험 범위 아님 |

## Gate A: Matching Response Happy Path

Evidence:

- [Gate A raw log](../../assets/logs/esp32_uart_bridge/2026-08-03_response_gated_startup_gate_a_pass.txt)

실제 순서:

| Event | Observed |
| --- | --- |
| Line sync | log line 4, `STARTUP: line sync sent` |
| DISARM request | `DISARM,seq=3121743592` |
| Matching ACK | `seq=3121743592`, `type=DISARM` |
| PING request | `PING,seq=3121743593` = `S+1` |
| Matching PONG | `seq=3121743593` |
| READY | 두 matching response 뒤에만 출력 |
| Motion traffic | `ARM/CMD` TX 0회 |
| Telemetry | 17개 모두 `DISARMED`, `vx=0`, `w=0` |

초기 line sync 직후 `RX_DESYNC` 1회가 기록됐지만 다음 정상 frame에서
복구됐고, matching response 순서와 fail-closed 상태를 깨지 않았다. 이 오류를
숨기거나 정상 통신 무오류 증거로 재해석하지 않는다.

또한 파일은 monitor `t_ms=800`, `tel_count=3`, `err=8`인 지점부터 시작하고 ESP
boot banner나 STM32 reset marker가 없다. 따라서 이 로그는 눈에 보이는 startup
transaction을 증명하지만 cold start 전체와 그 이전 오류 이력을 독립 증명하지 않는다.

판정: Gate A의 raw runtime behavior `PASS`.

## Gate B: Bounded Failure And Recovery

### DISARM ACK loss

Evidence:

- [DISARM ACK loss raw log](../../assets/logs/esp32_uart_bridge/2026-08-03_response_gated_startup_gate_b_bounded_failure_pass.txt)

동일한 `DISARM,seq=2597542306`이 monitor time `877`, `1377`, `1877 ms`에
총 3회 송신됐다. 간격은 각각 500 ms이고, `2377 ms`에
`STARTUP FAILED: no matching DISARM ACK`로 종료됐다. 네 번째 DISARM,
READY, ARM 또는 CMD는 없다. 이후 관찰된 telemetry 40개는 모두
`DISARMED`, `vx=0`, `w=0`이다.

판정: DISARM ACK 누락 bounded failure `PASS`.

### PONG loss

Evidence:

- [PONG loss raw log](../../assets/logs/esp32_uart_bridge/2026-08-03_response_gated_startup_gate_b2_no_pong_bounded_failure_pass.txt)

Startup DISARM `seq=1314481158`은 정확한 ACK를 받았다. 이어진
`PING,seq=1314481159`는 monitor time `877`, `1377`, `1887 ms`에 총 3회
송신됐고 `2387 ms`에 `STARTUP FAILED: no matching PONG`으로 종료됐다.
Monitor task timestamp의 마지막 간격은 510 ms지만 설계된 500 ms timeout과
task scheduling/로그 해상도 범위에서 관찰된 값이다. READY, ARM, CMD는 없고
telemetry 37개는 모두 `DISARMED`, zero velocity다.

판정: PONG 누락 bounded failure `PASS`.

### Controlled ESP reset / new-startup recovery

Evidence:

- [Reset recovery raw log](../../assets/logs/esp32_uart_bridge/2026-08-03_response_gated_startup_post_failure_reset_recovery_pass.txt)

STM32 uptime가 이어지는 상태에서 ESP32 startup이 다시 시작돼 새
`DISARM,seq=2580292164`, `PING,seq=2580292165`와 matching response를 받은 뒤
READY에 진입했다. ARM/CMD는 없고 telemetry는 계속 DISARMED/zero다.

이 로그는 `Waiting for device to reconnect` 뒤 ESP timestamp가 다시 시작되고 STM32
uptime은 이어지는 controlled ESP reset/new-startup recovery를 보여준다. 다만 파일
안에는 reset 직전의 `STARTUP FAILED`나 이전 session의 늦은 response가 포함돼 있지
않다. 따라서 `post-failure`라는 session 연결은 파일명/작업자 labeling에 의존하며,
이 raw 파일 단독으로 직전 failure 연속성이나 late-response rejection까지 증명하지
않는다. 전원 OFF 재배선 절차도 별도 작업자 확인이 필요하다.

판정: controlled ESP reset/new-startup recovery `PASS`; post-failure session linkage는
operator confirmation pending.

## Wrong Or Stale Response Rejection

두 파일의 이름에는 `gate_c1/c2`가 들어 있지만, 판정 의미는 Gate C의
malformed command recovery가 아니라 Gate B/T-BRIDGE-007의 wrong-response
rejection이다. 원본 증거 파일명은 변경하지 않고 의미를 이 보고서에서 바로잡는다.

| Vector | Expected | Observed | Result |
| --- | --- | --- | --- |
| Stale DISARM ACK seq | `S=1516921324`; `S-1`은 무시 | `1516921323` ACK 무시, 같은 DISARM retry 뒤 exact ACK와 READY | PASS |
| Stale PONG seq | expected `2914858155`; 이전 seq 무시 | `2914858154` PONG 무시, 같은 PING retry 뒤 exact PONG과 READY | PASS |
| Wrong ACK type | matching seq지만 `type != DISARM` 거부 | `type=ARM` 무시, 500 ms 뒤 같은 DISARM seq 재시도, exact ACK/PONG 뒤에만 READY | PASS |

Evidence:

- [Stale DISARM ACK raw log](../../assets/logs/esp32_uart_bridge/2026-08-03_response_gated_startup_gate_c1_stale_disarm_ack_rejection_pass.txt)
- [Stale PONG raw log](../../assets/logs/esp32_uart_bridge/2026-08-03_response_gated_startup_gate_c2_stale_pong_rejection_pass.txt)
- [Wrong DISARM ACK type raw log](../../assets/logs/esp32_uart_bridge/2026-08-04_response_gated_startup_wrong_disarm_ack_type_rejection_pass.txt)

두 stale-response 실행 모두 최종 matching response 전까지 READY에 진입하지
않았고 ARM/CMD를 송신하지 않았다. 전체 telemetry 43개는 모두
DISARMED/zero였다. Stale ACK 실행의 `BAD_TYPE`/`RX UNKNOWN`은 수신 정렬 과정의
오류로 기록돼 있으며 이후 정상 frame으로 복구됐다.

2026-08-04 후속 실행에서는 `DISARM,seq=1552695929`에 대한 matching-seq
`ACK,type=ARM`을 gate가 무시했다. 정확히 500 ms 뒤 같은 DISARM seq를 재시도했고,
`type=DISARM` ACK와 `PONG,seq=1552695930` 뒤에만 READY가 됐다. TEL 97/97은
DISARMED/zero였고 ARM/CMD TX와 `STARTUP FAILED`는 없었다.

판정: wrong-sequence와 matching-seq/wrong-type rejection을 포함한 T-BRIDGE-007
required UART runtime behavior `PASS`. Binary identity와 물리 setup provenance는
계속 별도 pending이다.

## Gate C 상태

2026-08-04 active-DISARM capture의 UART log에서 READY 이후 다음 controlled
normal sequence를 다시 확인했다.

```text
CMD before ARM -> NOT_ARMED
ARM -> ACK / ARMED
valid CMD -> ACK / vx=50
out-of-range CMD -> OUT_OF_RANGE, previous active command retained
DISARM -> ACK / DISARMED / zero
```

이 실행은 [active DISARM report](10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)에 기록한다.
반면 ESP32 startup-response parser에 malformed response를 넣은 뒤 exact response로
복구하는 T-BRIDGE-008A와, STM32 command parser가 malformed PING/CMD/unknown을
거부한 뒤 final valid PING/PONG으로 복구하는 T-BRIDGE-008B raw log는 모두 없다.
따라서 Gate C normal half는 `PASS`, 두 parser의 malformed/recovery half는
`NOT TESTED`, Gate C 전체는 `PARTIAL`이다.

## 현재 Source/Test 상태

2026-08-04 wrong-ACK-type 시험 뒤 실제 파일을 다시 읽은 current worktree 상태는 다음과 같다.

| Source setting | Current value |
| --- | ---: |
| ESP32 `BRIDGE_SCRIPTED_TEST_ENABLED` | `0U` |
| ESP32 `TEST_STEP_PERIOD_MS` | `1000` |
| STM32 `UART_MVP_OUTPUT_TEST_ENABLED` | `0U` |
| STM32 wrong DISARM ACK type once hook | `1U` |
| STM32 stale/suppress startup injection hooks | 모두 `0U` |
| STM32 button output/fault hooks | 모두 `0U` |

Wrong-type hook을 `0U`로 둔 structural checkpoint는 contract `15/15 PASS`, isolated
STM32 build `20260804144612-32776-5226` PASS다. 현재 controlled `1U` source는
default-off guard 한 건만 의도적으로 실패하며, STM32 test build
`20260804144706-1756-bc19`은 `0 errors / 0 warnings`로 PASS했다. Safe release 전에는
hook을 다시 `0U`로 복구하고 contract/build/reflash/runtime 회귀를 반복해야 한다.

## Evidence Integrity

| File | SHA-256 |
| --- | --- |
| Gate A | `be1767184328ea83dc566713309a7aa5127d76b6692308e665f3f5d962f0dc07` |
| DISARM ACK loss | `3d0b788c5fc246ecf5d424f830cadb75a031320fa058e4f8b2bcfad43e68247a` |
| PONG loss | `db66287c265a9b98816dc4e1dcb9d94ee7114765aad6144d9ed37372b4ce9085` |
| Stale DISARM ACK | `851e1821a54d22a3bdd2056008292d5a06bcc06019278f3523e9db9205c1a846` |
| Stale PONG | `a4e1e7e15881473dfc54618c388f0e91fab8fb7270ae18f802bffa935615d8f3` |
| Reset recovery | `83215d340f18fe2b43052122866622fe81446e33848bb4d62d4e503a828f5d29` |
| Wrong DISARM ACK type | `43d15b95427db5e46423a8138bd0f6017f7e9b152b623cddcd2401625415cbc8` |

## 결론과 다음 Gate

Gate A의 exact response sequence와 Gate B의 두 no-response bounded failure,
stale sequence 및 matching-seq/wrong-type 거부, reset recovery는 raw runtime behavior
기준으로 통과했다.
그러나 current UART release는 다음 항목 때문에 계속 `PARTIAL`이다.

1. Wrong-ACK-type hook을 `0U`로 복구하고 contract `15/15`와 safe STM32 build를 재확인한다.
2. Safe STM32 image를 board에 reflash/run한다.
3. Safe `0U` image에서 READY 뒤 ARM/CMD 무송신 회귀를 다시 확인한다.
4. Gate C에서 ESP startup-response parser와 STM32 command parser의 malformed
   reject/recovery를 각각 실행한다.
5. 작업자가 Gate A/B 당시 무전원 및 power-off rewiring 조건을 확인하면 시험
   provenance에 추가한다.

# 2026-08-03 UART Response-Gated Startup Implementation Handoff

> 이 문서는 구현 직후의 역사 checkpoint다. Gate A/B runtime과 active DISARM
> capture 이후 current continuation은
> [`2026-08-04_uart_runtime_and_active_disarm_handoff.md`](2026-08-04_uart_runtime_and_active_disarm_handoff.md)를 따른다.

This handoff superseded [`2026-08-03_uart_strict_parser_regression_handoff.md`](2026-08-03_uart_strict_parser_regression_handoff.md) at implementation time. It is now superseded by the 2026-08-04 handoff above.

## 현재 목표

ESP32-S3와 NUCLEO-F446RE 사이의 response-gated startup을 실제 보드에서 검증하고, malformed-frame fail-closed/recovery를 닫는다.

구현과 정적 검사는 완료됐지만 새 startup image의 flash/run 증거는 아직 없다. 현재 판정은 다음과 같다.

- implementation: `COMPLETE`
- firmware contract tests: `15/15 PASS`
- ESP32-S3 build: `PASS`
- board startup runtime: `NOT TESTED`
- malformed recovery board injection: `NOT TESTED`
- current strict-parser release: `PARTIAL`

## 구현된 설계

수정된 파일:

- `03_Firmware/esp32_uart_bridge/main/hello_world_main.c`
- `03_Firmware/tests/test_firmware_contract.py`

Startup constants:

| Contract | Value |
| --- | ---: |
| settle time | `500 ms` |
| newline sync 이후 대기 | `100 ms` |
| response timeout | `500 ms` |
| 단계별 최대 전송 횟수 | `3` |
| startup DISARM sequence | 부팅마다 `esp_random()`으로 정한 `S` |
| startup PING sequence | `S + 1` |
| scripted sequence start | `S + 2` |

State flow:

```text
SETTLE
-> newline boundary sync
-> SYNC_WAIT
-> RX buffer/line-state reset
-> DISARM,seq=S
-> WAIT_DISARM_ACK
-> matching ACK,seq=S,type=DISARM
-> PING,seq=S+1
-> WAIT_PONG
-> matching PONG,seq=S+1
-> READY

timeout at either response gate
-> resend the same request up to three total attempts
-> FAILED when attempts are exhausted
```

Parser state now records:

- exact `PONG,` prefix, parsed `seq`, and a PONG-valid flag
- exact `ACK,` prefix, parsed `seq`, parsed `type`, and an ACK-valid flag

The startup step accepts only the expected sequence and type while it is in the corresponding wait state. An early, stale, duplicated, or unrelated ACK/PONG cannot latch a future success or advance the state. Scripted ARM/CMD steps run only when both `BRIDGE_SCRIPTED_TEST_ENABLED != 0U` and startup state is `READY`.

추가 hardening:

- startup sequence는 부팅마다 달라져 이전 세션의 늦은 ACK/PONG과 충돌할 가능성을 낮춘다.
- startup frame과 종결 LF는 한 번의 UART write로 전송한다.
- UART write 또는 RX flush/reset 실패는 성공으로 간주하지 않고 `FAILED`로 닫힌다.
- required field의 중복, 정수 overflow, trailing comma와 frame 이름 부분 일치를 거부한다.
- overlong line, embedded CR, control byte, NUL 또는 DEL을 만나면 해당 line의 남은 byte를 LF까지 전부 버린 뒤 다음 frame boundary에서 다시 시작한다.
- 알 수 없는 추가 field는 protocol 확장을 위해 허용하되, 필수 field는 정확히 한 번 존재해야 한다.

## 설계 이유와 Safety Invariant

The previous fixed-delay preamble assumed that the peer had booted and that one PING would be received. The 2026-07-31 bench run showed that this assumption can fail because of stale sessions, first-frame loss, or UART line desynchronization.

The replacement uses observable responses rather than elapsed time as authority:

1. Newline creates a line boundary after possible partial RX data.
2. Explicit DISARM first establishes a fail-safe peer state.
3. A matching DISARM ACK proves that the peer accepted that exact safety request.
4. A matching PONG proves bidirectional communication after synchronization.
5. Only then does the state become READY.

Safety invariants:

- READY is unreachable without both matching responses.
- ARM/CMD scripted traffic is blocked before READY.
- Retry is bounded; silence cannot cause an infinite command loop.
- Retry exhaustion ends in `STARTUP_FAILED`, not an assumed success state.
- `BRIDGE_SCRIPTED_TEST_ENABLED=0U` still permits the safe DISARM/PING handshake but does not send scripted ARM/CMD commands.
- The optional `1U` scripted ARM/CMD/DISARM sequence is timing-driven after READY; it does not wait for an ACK at every motion step. Treat it only as a motor-disconnected controlled regression, not as a production command sequencer.

## Static and Build Evidence

- firmware contract suite: `15/15 PASS`
- ESP32-S3 build: `PASS`
- application binary: `0x2b210` bytes
- smallest app partition free: `83%`
- source default: `BRIDGE_SCRIPTED_TEST_ENABLED=0U`

The 15 tests combine host parser vectors with source/configuration contract checks. They are not an executable host proof of every branch in the ESP32 FSM/parser. Together with the build, they prove source-level contracts and compilation only; they do not prove response timing, retry behavior, board UART behavior, motor output, or electrical safety.

## Source and Board State

Source defaults:

- ESP32 `BRIDGE_SCRIPTED_TEST_ENABLED=0U`
- STM32 `MOTOR_OUTPUT_PIN_TEST_ENABLED=0U`
- STM32 `MOTOR_FAULT_INJECTION_TEST_ENABLED=0U`
- STM32 `UART_MVP_OUTPUT_TEST_ENABLED=0U`

The new ESP32 source has not yet been flashed and run for runtime evidence. The ESP32 board may still contain the earlier controlled-test `1U` image. Do not describe the board as restored to a safe image until the `0U` build is actually flashed and its boot behavior is observed.

## 다음 세션 첫 확인

저장소 루트 `C:\Users\eyh12\workspace\TIL`에서 시작한다.

```powershell
git status --short -- Projects/Tracked_Mobile_Robot

python -m unittest discover `
  -s Projects/Tracked_Mobile_Robot/03_Firmware/tests `
  -p "test_*.py" `
  -v
```

Then inspect the actual diff before modifying files. Preserve the user's current changes.

## Runtime Gate A: Safe `0U` Startup

Preconditions:

1. LiPo disconnected.
2. MDD10A B+/B- and actual motor power disconnected.
3. ESP32 and STM32 test macros confirmed `0U`.
4. UART remains `ESP GPIO17 TX -> STM PA10 RX`, `ESP GPIO18 RX <- STM PA9 TX`, common GND, `115200 8-N-1`.
5. If both boards are USB-powered, do not connect their `5 V`, `VBUS`, or `VIN` rails.

The user performs physical wiring, flash, and power operations. Before each action, state the exact expected log and the stop condition.

Expected first boot sequence:

```text
STARTUP: line sync sent
TX UART1: DISARM,seq=<S>
RX ACK: seq=<S> type=DISARM ack_count=<n>
STARTUP: DISARM acknowledged
TX UART1: PING,seq=<S+1>
RX PONG: seq=<S+1> pong_count=<n>
STARTUP READY: DISARM ACK and PONG verified
```

`<S>`는 부팅 때마다 달라질 수 있다. 숫자 자체를 고정값과 비교하지 말고, 실제 TX의 DISARM sequence와 RX ACK가 같고 실제 TX PING이 그 다음 값이며 RX PONG과 같은지를 비교한다.

With the macro at `0U`, no ARM or CMD frame may follow. Save the raw monitor log under `assets/logs/esp32_uart_bridge/` with a dated, test-specific filename.

PASS criteria:

- ACK sequence and type match exactly.
- PONG sequence matches exactly.
- READY appears only after those two matches.
- no ARM/CMD is transmitted.
- telemetry remains DISARMED with zero velocity.

## Runtime Gate B: Bounded Failure

Change physical signal connections only while board power is off. Create a controlled no-response condition and prove:

- the active startup request is sent no more than three total attempts
- state becomes `STARTUP_FAILED`
- no ARM/CMD frame is transmitted
- restoring the peer requires a controlled reset/new startup, not an implicit late transition

Capture the complete retry-to-failure log. Do not energize MDD10A or a motor for this test.

## Runtime Gate C: Normal Sequence and Malformed Recovery

Only after Gate A and Gate B pass, a motor-disconnected controlled build may temporarily set `BRIDGE_SCRIPTED_TEST_ENABLED=1U` to rerun the normal sequence. This timing-driven script does not gate every motion step on its ACK, so do not connect motor power and do not treat it as production behavior. Restore it to `0U` immediately after capture.

While the STM32 remains DISARMED, use these malformed/recovery vectors:

```text
DISARM,seq=100
PING,seq=101,extra=1
CMD field order violation with seq=102
BAD,seq=103
PING,seq=104
```

PASS criteria:

- malformed PING, invalid-order CMD, and unknown frame are not executed
- each invalid input is rejected fail-closed
- telemetry remains DISARMED with zero velocity
- the final valid `PING,seq=104` receives `PONG,seq=104`
- no RX overflow or unrecovered line desynchronization remains

## 종료 복구와 증빙 루틴

1. Restore `BRIDGE_SCRIPTED_TEST_ENABLED=0U`.
2. Run all firmware contract tests.
3. Run clean STM32/ESP32 builds as applicable.
4. Flash and run the ESP32 safe `0U` image.
5. Confirm no scripted ARM/CMD after READY.
6. Preserve raw logs first; screenshots are secondary evidence.
7. Update progress, verification, handoff, `PROJECT_MEMORY.md`, and indexes without overstating the evidence boundary.
8. Run `git diff --check`, review `git diff` and `git status`.
9. Commit and push only the intended files when the user requests it. Never include build directories, credentials, tokens, or unrelated user changes.

## 작업 방식

- Firmware learning defaults to one small block typed by the user, followed by a reread of the saved file.
- If the user explicitly says `너가 추가해`, `너가 수정해`, or `직접 진행해`, Codex edits only that delegated scope.
- `확인해봐` means reread the real file and verify exact placement, text, control flow, compile impact, and safety implications.
- Every code explanation must cover the problem, design reason, structure and responsibilities, control/data flow, normal and failure paths, safety invariants, alternatives/tradeoffs, and verification/PASS criteria.

## 건드리면 안 되는 결정

- STM32 remains parser, command-timeout, motor-output, encoder, and final safety authority.
- ESP32 remains command source, relay/logger, and future wireless bridge candidate.
- Do not change the validated UART pin/baud mapping.
- Do not connect the two boards' 5 V rails when each is USB-powered.
- Do not apply battery, MDD10A, or actual motor power during these UART gates.
- Do not treat static tests/builds as board-runtime or electrical PASS.
- Do not overwrite the historical normal-sequence report with the new runtime result; create new dated evidence/reporting for the response-gated implementation.

## 완료 조건

This UART release gate closes only when all of the following are evidenced:

- successful response-gated startup
- exact matching ACK/PONG behavior
- bounded retry and fail-closed startup failure
- no ARM/CMD before READY or after FAILED
- normal controlled sequence after READY
- malformed-frame rejection and final valid-frame recovery
- source macro restored to `0U`
- contract tests and builds pass
- safe `0U` image is flashed and run
- raw logs and scoped verification documentation are preserved

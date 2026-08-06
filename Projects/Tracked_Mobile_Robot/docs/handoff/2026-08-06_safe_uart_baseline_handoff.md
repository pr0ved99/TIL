# 2026-08-06 Safe UART Baseline Handoff

This handoff supersedes [`2026-08-04_uart_runtime_and_active_disarm_handoff.md`](2026-08-04_uart_runtime_and_active_disarm_handoff.md) as the current UART continuation source.

## Current Objective

The wrong-ACK controlled test is closed. Current safe source/static/build and the separately observed safe UART behavior are both PASS within their evidence boundaries. The next technical gate is T-BRIDGE-008 Gate C two-parser malformed-frame rejection and recovery.

```text
Gate A exact startup: PASS
Gate B bounded loss/stale response/reset recovery: PASS behavior
T-BRIDGE-007 wrong ACK rejection/same-seq retry: PASS behavior
Active DISARM MCU-pin first baseline: PASS, 23.50 us
2026-08-06 current safe source/static/build: PASS
2026-08-06 observed safe UART runtime behavior: PASS; exact linkage/setup provenance pending
Gate C ESP-response parser recovery: NOT TESTED
Gate C STM32-command parser recovery: NOT TESTED
Current UART release: PARTIAL
```

## Current Actual Source State

| Macro/setting | Value |
| --- | ---: |
| ESP `BRIDGE_SCRIPTED_TEST_ENABLED` | `0U` |
| ESP `TEST_STEP_PERIOD_MS` | `1000` |
| STM `UART_MVP_OUTPUT_TEST_ENABLED` | `0U` |
| STM stale DISARM ACK hook | `0U` |
| STM wrong DISARM ACK type hook | `0U` |
| STM stale/suppressed PONG hooks | `0U` |
| STM motor-output/fault button hooks | `0U` |

The restored hook is the only firmware source change relative to commit `51e3fc9`:

```c
#define UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED 0U
```

## Completed Safe Baseline

- Firmware contract: `15/15`, `OK`.
- STM32CubeIDE build: user reported `0 errors / 0 warnings`.
- Local ELF: `1,239,972 bytes`, modified `2026-08-06 17:02:37.995`.
- ELF SHA-256: `71EF2C275A5DD5CFAB34995D1CF33A76B4DC4593661842BD6E379D6DBEFACBAF`.
- Final board log: exact DISARM ACK and PONG before READY, 11.35 s after READY, TEL 120/120 `DISARMED/zero/error 0`, ARM/CMD 0 and parser/startup errors 0.

## Evidence

- [2026-08-06 progress](../progress/2026-08-06_progress.md)
- [Final safe-image UART regression](../../assets/logs/esp32_uart_bridge/2026-08-06_safe_image_uart_runtime_regression_pass.txt)
- [Preliminary 10 s total observation](../../assets/logs/esp32_uart_bridge/2026-08-06_safe_image_uart_runtime_regression_run1_10s_total.txt)
- [UART evidence index and hashes](../../assets/logs/esp32_uart_bridge/README.md)
- [Response-gated startup report](../verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md)
- [Active DISARM latency report](../verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)

## Evidence Boundary

The saved UART logs do not contain the flash transcript, physical no-power setup metadata or an embedded binary hash. Therefore the exact ELF-to-board linkage and LiPo/MDD10A/motor-power separation remain operator/provenance pending. Do not extend the PASS to MDD10A output, actual motor stop, Physical E-stop or electrical behavior.

## Next Gate: T-BRIDGE-008A

Start with one controlled response vector: on the first DISARM request, STM32 sends an ACK containing duplicate `seq` fields; on the retry it sends the normal exact ACK. ESP32 must reject the malformed response, remain in `WAIT_DISARM_ACK`, retry the same sequence after 500 ms and reach READY only after the exact ACK and matching PONG.

PASS criteria:

- The malformed ACK does not produce `DISARM acknowledged`, PING or READY.
- The same DISARM sequence is retried after about 500 ms.
- Only the exact `ACK(seq=S,type=DISARM)` and `PONG(seq=S+1)` open READY.
- All telemetry remains `DISARMED` with zero command/CPS values and `err=0`.
- There is no `TX ARM`, `TX CMD`, unrecovered overflow/desync, reset loop or `STARTUP FAILED`.
- This first vector alone does not close all of T-BRIDGE-008A; overflow, trailing comma, partial-name, terminator/control and overlong vectors remain.

## Safety Preconditions

- LiPo, MDD10A B+/B- and actual motor power stay disconnected.
- With both boards USB-powered, do not connect their 5 V/VBUS/VIN rails.
- Keep UART crossed and common GND: ESP GPIO17 TX -> STM32 PA10 RX; ESP GPIO18 RX <- STM32 PA9 TX.
- The user performs firmware edits, build, flash, reset and physical actions; Codex supplies small blocks, exact locations and PASS criteria, then rereads saved files.
- After every controlled hook, restore all hooks to `0U`, require `15/15`, rebuild/reflash and repeat the safe runtime regression.

## Git And Workspace Note

Current branch is `agent/dual-encoder-bringup`. CubeIDE-generated changes in `.settings/language.settings.xml` and `stm32_uart_mvp Debug.launch` are unrelated to the safe baseline and must not be staged with it.

## First Check In A New Session

```powershell
git status --short -- Projects/Tracked_Mobile_Robot
```

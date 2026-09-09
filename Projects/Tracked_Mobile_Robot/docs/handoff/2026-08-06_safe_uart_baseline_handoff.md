# 2026-08-06 Safe UART Baseline Handoff

This handoff supersedes [`2026-08-04_uart_runtime_and_active_disarm_handoff.md`](2026-08-04_uart_runtime_and_active_disarm_handoff.md) as the current UART continuation source.

## Current Objective

The wrong-ACK controlled test and the T-BRIDGE-008A duplicate-required-`seq`, trailing-comma and
required-`seq` uint32-overflow response vectors are closed. Each controlled cycle was followed by
an all-hooks-`0U` restore, static checks, safe reflash and UART regression. The next technical gate
is the remaining T-BRIDGE-008A ESP response-parser vectors, starting with an isolated partial frame
name.

```text
Gate A exact startup: PASS
Gate B bounded loss/stale response/reset recovery: PASS behavior
T-BRIDGE-007 wrong ACK rejection/same-seq retry: PASS behavior
Active DISARM MCU-pin first baseline: PASS, 23.50 us
2026-08-07 post-overflow safe source/static/protocol recompile+relink 0/0/reflash: PASS
2026-08-07 post-overflow safe UART runtime behavior: PASS; exact linkage/setup provenance pending
Gate C ESP-response parser recovery: PARTIAL — duplicate required seq + trailing comma + required-seq uint32 overflow PASS
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
| STM duplicate DISARM ACK `seq` hook | `0U` |
| STM trailing-comma DISARM ACK hook | `0U` |
| STM required-`seq` uint32-overflow DISARM ACK hook | `0U` |
| STM stale/suppressed PONG hooks | `0U` |
| STM motor-output/fault button hooks | `0U` |

The current uncommitted firmware changes include three dedicated one-shot malformed-response hooks.
All are disabled in the safe source:

```c
#define UART_MVP_DUPLICATE_DISARM_ACK_SEQ_ONCE_TEST_ENABLED 0U
#define UART_MVP_TRAILING_COMMA_DISARM_ACK_ONCE_TEST_ENABLED 0U
#define UART_MVP_OVERFLOW_DISARM_ACK_SEQ_ONCE_TEST_ENABLED 0U
```

## Completed Evidence Chain

- Pre-008A safe contract: `15/15`, `OK`.
- Pre-008A STM32CubeIDE build: user reported `0 errors / 0 warnings`.
- Pre-008A historical ELF: `1,239,972 bytes`, modified `2026-08-06 17:02:37.995`, SHA-256 `71EF2C275A5DD5CFAB34995D1CF33A76B4DC4593661842BD6E379D6DBEFACBAF`.
- Pre-008A board log: exact DISARM ACK and PONG before READY, 11.35 s after READY, TEL 120/120 `DISARMED/zero/error 0`, ARM/CMD 0 and parser/startup errors 0.
- Duplicate-`seq` controlled ELF: SHA-256 `9565A1405FF97BE75BC1D30F87DEBD1CE32ED05D8E16525D2205231AD74CCA61`; branch string present; flash verify PASS.
- Duplicate-`seq` runtime: malformed ACK rejected once, same DISARM seq retried after exactly 500 ms, exact ACK/PONG only then READY; TEL 150/150 safe.
- Post-test safe ELF: `1,240,148 bytes`, SHA-256 `25885322BD28B19456498A37C14B87D039984A96F2E2EA30CC1764A36E086A2A`; branch string absent; flash verify PASS.
- Post-test safe runtime: retry/parser error 0, exact startup, 14.42 s after READY, TEL 150/150 safe, ARM/CMD 0.
- Trailing-comma controlled ELF: `1,240,348 bytes`, SHA-256 `5791C9B1E5A8F2ED942B8A8A0BDD8599C2A775EDB5D59022E60CE900C52B406E`; controlled string present in object/ELF/list; flash verify PASS.
- Trailing-comma runtime: terminal comma rejected once, same DISARM seq retried after exactly 500 ms, exact ACK/PONG only then READY; TEL 150/150 safe.
- Post-trailing safe ELF: `1,240,328 bytes`, SHA-256 `3526206C7E2043634029B15B7D41F9C80B136904FCA72FB46D8CA24F4119DEE4`; controlled string absent from object/ELF/map/list; flash verify PASS. A post-Clean full build recompiled all 31 objects and linked with `0 errors / 0 warnings`, reproducing the retained safe hashes exactly.
- Post-trailing safe runtime: warning/retry/parser error 0, exact startup, 15.51 s after READY, TEL 160/160 safe, ARM/CMD 0.
- Required-`seq` uint32-overflow controlled ELF: `1,240,520 bytes`, SHA-256 `747F32E3BDFBF0D4130E2F136145806AE88FF4F94BBC8948C7FFB554BE0A3701`; literal overflow response string present; flash verify PASS.
- Required-`seq` uint32-overflow runtime: `seq=4294967296` rejected once, same DISARM seq retried after exactly 500 ms, exact ACK/PONG only then READY; complete post-READY TEL 140/140 safe, ARM/CMD/failure 0.
- Current safe ELF: `1,240,504 bytes`, SHA-256 `244DD5D31192591AA35866D7529FF7596D3A56CE87E0596F34BFFDBB459E5F6B`; `uart_mvp_protocol.c` was recompiled and the ELF relinked with `0 errors / 0 warnings`; controlled string absent from object/ELF/map/list; flash verify PASS.
- Current safe runtime: warning/retry/parser error 0, exact startup, 14.43 s after READY, complete post-READY TEL 145/145 safe, ARM/CMD 0.

## Evidence

- [2026-08-06 progress](../progress/2026-08-06_progress.md)
- [Final safe-image UART regression](../../assets/logs/esp32_uart_bridge/2026-08-06_safe_image_uart_runtime_regression_pass.txt)
- [Preliminary 10 s total observation](../../assets/logs/esp32_uart_bridge/2026-08-06_safe_image_uart_runtime_regression_run1_10s_total.txt)
- [Duplicate required-seq controlled runtime](../../assets/logs/esp32_uart_bridge/2026-08-06_response_gated_startup_duplicate_required_seq_ack_rejection_recovery_pass.txt)
- [Post-duplicate safe UART regression](../../assets/logs/esp32_uart_bridge/2026-08-06_post_t_bridge_008a_duplicate_seq_safe_uart_runtime_regression_pass.txt)
- [Controlled/safe build and flash record](../../assets/logs/firmware_build/2026-08-06_t_bridge_008a_duplicate_seq_ack_controlled_and_safe_build_flash.md)
- [Duplicate-required-seq verification report](../verification/11_ESP32_Duplicate_Required_Seq_ACK_Recovery_Test_Report_2026-08-06_ko.md)
- [2026-08-07 progress](../progress/2026-08-07_progress.md)
- [Trailing-comma controlled runtime](../../assets/logs/esp32_uart_bridge/2026-08-06_response_gated_startup_trailing_comma_ack_rejection_recovery_pass.txt)
- [Post-trailing-comma safe UART regression](../../assets/logs/esp32_uart_bridge/2026-08-07_post_t_bridge_008a_trailing_comma_safe_uart_runtime_regression_pass.txt)
- [Trailing-comma controlled/safe build and flash record](../../assets/logs/firmware_build/2026-08-07_t_bridge_008a_trailing_comma_ack_controlled_and_safe_build_flash.md)
- [Post-Clean safe full-build console](../../assets/logs/firmware_build/2026-08-07_post_t_bridge_008a_trailing_comma_safe_clean_build_pass.txt)
- [Trailing-comma verification report](../verification/12_ESP32_Trailing_Comma_ACK_Recovery_Test_Report_2026-08-07_ko.md)
- [Required-seq uint32-overflow controlled runtime](../../assets/logs/esp32_uart_bridge/2026-08-07_response_gated_startup_required_seq_uint32_overflow_ack_rejection_recovery_pass.txt)
- [Post-overflow safe UART regression](../../assets/logs/esp32_uart_bridge/2026-08-07_post_t_bridge_008a_required_seq_uint32_overflow_safe_uart_runtime_regression_pass.txt)
- [Required-seq uint32-overflow controlled/safe build and flash record](../../assets/logs/firmware_build/2026-08-07_t_bridge_008a_required_seq_uint32_overflow_ack_controlled_and_safe_build_flash.md)
- [Required-seq uint32-overflow verification report](../verification/13_ESP32_Required_Seq_Uint32_Overflow_ACK_Recovery_Test_Report_2026-08-07_ko.md)
- [UART evidence index and hashes](../../assets/logs/esp32_uart_bridge/README.md)
- [Response-gated startup report](../verification/09_ESP32_STM32_UART_Response_Gated_Startup_Test_Report_2026-08-03_ko.md)
- [Active DISARM latency report](../verification/10_STM32_Active_DISARM_Shutdown_Latency_Test_Report_2026-08-04_ko.md)

## Evidence Boundary

The controlled and restored images were built and flash-verified sequentially, with hashes and
compiled-string presence/absence recorded. The trailing-comma and required-`seq` uint32-overflow
controlled/safe source and binary snapshots are retained outside Git. The latest safe build was an
incremental build that explicitly recompiled `uart_mvp_protocol.c` and relinked the ELF; it was not
a post-Clean full build. The saved UART logs still do not embed a binary hash, and
physical no-power setup metadata is not independently present. LiPo/MDD10A/motor-power separation
therefore remains operator-confirmation pending. Raw CubeProgrammer temporary logs were gone when
checked. The later safe full-build console is retained and proves source-to-ELF `0 errors / 0 warnings`
plus byte-identical artifact reproduction, but does not itself record a new flash. Do not extend the PASS to MDD10A output,
actual motor stop, Physical E-stop or electrical behavior. The earlier duplicate controlled ELF
was overwritten before independent retention; its hash and string-presence result remain a
sequential inspection record.

## Completed T-BRIDGE-008A Subvectors

The first DISARM request produced an ACK containing duplicate required `seq` fields. ESP32 rejected
it, stayed gated, retried the same sequence exactly 500 ms later and reached READY only after the
exact ACK and matching PONG. All criteria below passed.

PASS criteria:

- The malformed ACK does not produce `DISARM acknowledged`, PING or READY.
- The same DISARM sequence is retried after about 500 ms.
- Only the exact `ACK(seq=S,type=DISARM)` and `PONG(seq=S+1)` open READY.
- All telemetry remains `DISARMED` with zero command/CPS values and `err=0`.
- There is no `TX ARM`, `TX CMD`, unrecovered overflow/desync, reset loop or `STARTUP FAILED`.
- The trailing-comma vector repeated the same fail-closed behavior: one malformed-field-list warning, exact 500 ms same-seq retry, exact ACK/PONG-only READY and TEL 150/150 safe.
- The required-`seq` uint32-overflow vector rejected `seq=4294967296` once, retried the same DISARM seq after exactly 500 ms and opened READY only after the exact ACK/PONG; complete post-READY TEL 140/140 remained safe.
- These three vectors do not close all of T-BRIDGE-008A; partial frame name, invalid terminator/control and overlong-line/RX-line-overflow vectors remain.

## Next Gate: T-BRIDGE-008A Partial Frame Name

Inject exactly one response whose frame name is only a non-exact prefix/suffix variant of the
required ACK frame, then emit the normal exact ACK on the same-seq retry. Preserve the same safety
and recovery criteria used by the completed vectors. This closes only the partial-frame-name
subvector; invalid terminator/control and overlong-line/RX-line-overflow vectors still remain
afterward.

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

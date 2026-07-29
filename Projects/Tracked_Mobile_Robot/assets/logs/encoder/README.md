# Encoder Logs

## 2026-07-30 output-shaft calibration and mRPM validation

- Verification summary: [`2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md`](2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md)
- 50-revolution operator record: [`2026-07-30_50rev_output_shaft_calibration_operator_record.txt`](2026-07-30_50rev_output_shaft_calibration_operator_record.txt)
- Operator-record SHA-256: `CDCED10359EEB8D9B84BA9660A6772E4849A22C59005EC3D575139C0C4577377`
- Dynamic raw log: [`2026-07-30_dual_encoder_millirpm_hand_rotation_pass.txt`](2026-07-30_dual_encoder_millirpm_hand_rotation_pass.txt)
- Raw log SHA-256: `D16925EE4331B04726AB54BBBF1640DF72D852684E87B0EFD6C1B46C3AF1636B`
- Operator-reported 50-revolution counts:
  motor A CW `77,998`, A CCW absolute `78,001`, motor B CW/CCW absolute `78,000/78,000`
- Adopted STM32 quadrature x4 scale: `1560 counts/output rev`
- Runtime conversion: `mRPM = trunc(CPS * 60000 / 1560)`
- Boot self-test: `ENC_SELF_TEST,wrap=PASS,millirpm=PASS`
- Dynamic audit: 305 complete dual rows, 610 channel samples, malformed 0,
  calculation/sign/continuity mismatch 0 and final 26 rows stopped at zero

Decision:

- 50-revolution output-shaft scale calibration: `PASS`
- Dual hand-rotation CPS -> mRPM functional conversion: `PASS`
- Production `TEL` intentionally remains signed `left_cps/right_cps`; mRPM is a
  USART2 bench diagnostic field
- Powered-motor noise, vehicle left/right/forward sign, external physical-RPM
  reference and wheel-speed conversion: `NOT TESTED`
- This section supersedes only the provisional scale gap in the dated 2026-07-26
  through 2026-07-29 sections below; their historical test conclusions remain intact.
- The 50-revolution record is reconstructed from operator reports and is explicitly
  not represented as a device raw serial capture.

## 2026-07-29 production dual-CPS telemetry validation

- Verification summary: [`2026-07-29_dual_encoder_cps_uart_telemetry_verification.md`](2026-07-29_dual_encoder_cps_uart_telemetry_verification.md)
- Clean-reset/stationary TEL: [`2026-07-29_dual_encoder_cps_tel_stationary_clean_reset_pass.txt`](2026-07-29_dual_encoder_cps_tel_stationary_clean_reset_pass.txt)
- Clockwise TEL: [`2026-07-29_dual_encoder_cps_tel_cw_pass.txt`](2026-07-29_dual_encoder_cps_tel_cw_pass.txt)
- Counter-clockwise TEL: [`2026-07-29_dual_encoder_cps_tel_ccw_pass.txt`](2026-07-29_dual_encoder_cps_tel_ccw_pass.txt)
- Runtime path: STM32 TIM3/TIM5 -> wrap-safe CPS -> production UART `TEL` -> ESP32 parse/log
- Bench mapping established by the operator-controlled independent sequence:
  motor A -> TIM5 -> `right_cps`, motor B -> TIM3 -> `left_cps`
- Both motors: output-shaft-end clockwise produced positive CPS and
  counter-clockwise produced negative CPS.
- The inactive field remained zero while the other motor was moved, and both
  fields returned to zero after motion.
- Vehicle left/right and forward-positive mapping remains TBD. The production
  field mapping is therefore provisional and must not be treated as the final
  installed drivetrain assignment.

Decision:

- Main-power-on, output-hook-disabled manual-rotation production CPS telemetry end-to-end: `PASS`
- Vehicle mapping, exact speed calibration and powered-motor noise: `NOT TESTED`

## 2026-07-29 wrap-safe delta and counts/s validation

Evidence:

- Stationary log: [`2026-07-29_encoder_speed_stationary_pass.txt`](2026-07-29_encoder_speed_stationary_pass.txt)
- Stationary log SHA-256: `C1EBE65BCC19CD32B028E62FFA41A70AC0955CB59986069AFB66E59CBE880639`
- Hand-rotation log: [`2026-07-29_dual_encoder_speed_hand_rotation_pass.txt`](2026-07-29_dual_encoder_speed_hand_rotation_pass.txt)
- Hand-rotation log SHA-256: `1AC347D002133D9AF7C7A50C88B0010C48FCFA8A9E93FF71A7BBF5201D6A5FA9`
- Firmware module: [`../../../03_Firmware/stm32_uart_mvp/Core/Inc/encoder_speed.h`](../../../03_Firmware/stm32_uart_mvp/Core/Inc/encoder_speed.h), [`../../../03_Firmware/stm32_uart_mvp/Core/Src/encoder_speed.c`](../../../03_Firmware/stm32_uart_mvp/Core/Src/encoder_speed.c)
- Sample period: nominal `100 ms`
- Counter widths: TIM3 `16-bit`, TIM5 `32-bit`
- Motor power: disconnected; encoder rail and common GND remained connected
- Log transport: STM32 USART2 / ST-LINK VCP `COM3`, 115200 8N1

Boot synthetic self-test covered both count directions across both wrap points.

| Counter | Forward wrap vector | Expected/observed delta | Reverse wrap vector | Expected/observed delta |
| --- | --- | ---: | --- | ---: |
| 16-bit | `65530 -> 5` | `+11 / +11` | `5 -> 65530` | `-11 / -11` |
| 32-bit | `0xFFFFFFFA -> 5` | `+11 / +11` | `5 -> 0xFFFFFFFA` | `-11 / -11` |

Runtime output reported `ENC_SELF_TEST,wrap=PASS` before the periodic rows.

Stationary-log result:

| Counter | Parsed rows | Nonzero delta | Final total | Result |
| --- | ---: | ---: | ---: | --- |
| TIM3 | 146 | 0 | 0 | PASS |
| TIM5 | 146 | 0 | 0 | PASS |

One additional `ENC3`-prefixed text fragment in the captured stationary file did
not match the complete dual-row grammar and is excluded from the parsed-row
count. All 146 complete rows were stationary.

Hand-rotation result:

| Counter | Rows | Nonzero rows | Delta range | CPS range | Final accumulated count | Directions |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| TIM3 | 331 | 84 | `-62 .. +95` | `-620 .. +950` | `+358` | `NEG`, `POS`, `STOP` |
| TIM5 | 331 | 98 | `-60 .. +72` | `-600 .. +720` | `+1490` | `NEG`, `POS`, `STOP` |

At the nominal 100 ms sampling interval, the observed CPS was consistently the
sample delta multiplied by ten. Each counter remained at zero while only the
other encoder moved during the independent portions of the capture. Occasional
single-count changes near motion start/stop did not persist during the stable
stationary sections.

Decision:

- 16/32-bit modular delta synthetic wrap cases: `PASS`
- Dual motor-off runtime accumulation and count/s direction changes: `PASS`
- Stationary false-count subtest: `PASS`
- Production UART `TEL` integration: `PASS` in the later end-to-end subtest
  documented at the top of this index
- Exact CPR, wheel speed conversion, vehicle sign and powered-motor noise: `NOT TESTED`

The firmware keeps delta, accumulated count and counts/s as `int64_t`. The
current newlib-nano USART2 bench logger prints values through `(long)`/`%ld` only
because this short capture remains inside the 32-bit display range; this does
not narrow the internal accumulator.

## 2026-07-27 TIM3/TIM5 dual independent hand-rotation test

- Raw serial log: [`2026-07-27_tim3_tim5_dual_encoder_independent_hand_rotation_raw.txt`](2026-07-27_tim3_tim5_dual_encoder_independent_hand_rotation_raw.txt)
- Source attachment SHA-256: `4A73CBD34D0CE5966CF722EFE9E95EFF13C9F1DB9BFE6A2EA176FB8D34F05685`
- Repository-copy SHA-256: `9DB9A5CABCDABF23DF2A6235B835C3159EAA80A55A819378BD5B7DEF2693BCD1`
- Parsed log rows: 141
- MCU: NUCLEO-F446RE
- Encoder input 1: `PB4/TIM3_CH1 = A`, `PB5/TIM3_CH2 = B`
- Encoder input 2: `PA0/TIM5_CH1 = A`, `PA1/TIM5_CH2 = B`
- Timer mode: both `TIM_ENCODERMODE_TI12`, x4 quadrature count
- Initial counter: TIM3 `32768`, TIM5 `0x80000000`
- Signal conditioning per channel: encoder signal -> 1 kΩ series -> STM32 input node, with 15 kΩ from that node to common GND
- Encoder supply: XL4015 #2 5 V rail; STM32, both encoders and XL4015 grounds common
- Motor power: disconnected
- Log transport: STM32 USART2 / ST-LINK VCP `COM3`, 115200 8N1

The repository copy normalizes the attachment's CRLF line endings to LF and
adds one final newline. After line-ending and final-newline normalization, all
141 serial rows are identical to the source attachment.

Raw-log observations:

| Phase | Active counter | Observed count range | Inactive counter | Result |
| --- | --- | ---: | --- | --- |
| First hand rotation and return | ENC5 / TIM5 | `0 -> +1557 -> -6` | ENC3 remained `0` | Independent count and reversal PASS |
| Second hand rotation and return | ENC3 / TIM3 | `0 -> +1561 -> +7` | ENC5 remained `-6` | Independent count and reversal PASS |

The user separately reported a one-output-shaft-turn result of `+1555 / -1566`
for the newly tested encoder path, and confirmed that the previously tested
encoder reproduced its expected result. Those exact values are operator
observations from the same bench session; the raw file demonstrates the
increment/decrement trajectory and inactive-channel stability rather than
containing those two values as isolated endpoints.

The shaft was turned by hand without a mechanical 360-degree index fixture.
Start/end alignment, slight overrun and gearbox backlash therefore limit the
one-revolution accuracy. These values support an approximate `1560 count/rev`
bring-up scale, not an exact encoder CPR calibration. Final calibration should
use a marked reference and multiple revolutions before dividing the total
count by the revolution count.

Decision:

- TIM3/TIM5 dual motor-off independent count/sign subtest: `PASS`
- Provisional scale: `1560 counts/output rev`
- As of the 2026-07-27 checkpoint, overall encoder verification remained
  `PARTIAL` because vehicle physical left/right/forward sign, exact output-shaft
  calibration and powered-motor noise were still unverified. The 2026-07-30
  section above closes the output-shaft calibration gap only.

## 2026-07-26 TIM3 motor-off hand-rotation test

- Raw serial log: [`2026-07-26_tim3_mg540a_bidirectional_hand_rotation_raw.txt`](2026-07-26_tim3_mg540a_bidirectional_hand_rotation_raw.txt)
- Raw log SHA-256: `ED11CA95A1218A485A42ED82B300C619459F8BEBAB904C2C9B43E54DA7B3D7AD`
- MCU: NUCLEO-F446RE
- Timer input: `PB4/TIM3_CH1 = A`, `PB5/TIM3_CH2 = B`
- Timer mode: `TIM_ENCODERMODE_TI12`, x4 quadrature count, 16-bit polling
- Signal conditioning per channel: encoder signal -> 1 kΩ series -> STM32 input node, with 15 kΩ from that node to common GND
- Encoder supply: XL4015 5 V rail; STM32, encoder and XL4015 grounds common
- Motor power: disconnected
- Log transport: STM32 USART2 / ST-LINK VCP `COM3`, 115200 8N1

The MG540-A filename/assignment comes from the bench-session notes; the raw
text itself does not contain a motor ID. The raw log shows a stable stationary count, increasing count in one shaft
direction and decreasing count after reversal. The exact one-output-shaft-turn
results were reported separately during the same bench session:

| Bench motor | Clockwise | Counter-clockwise | Provisional counts/output rev |
| --- | ---: | ---: | ---: |
| MG540-A | +1560 | -1560 to -1570 | 1560 |
| MG540-B | +1562 | -1560 | 1560 |

Clockwise/counter-clockwise are defined while looking directly at the output
shaft end. These signs belong to the bench wiring orientation and are not yet
the vehicle-forward sign. At the close of the 2026-07-26 session, TIM5 was
unverified; the 2026-07-27 section above supersedes that item. Powered-motor
noise behavior, hardware input filtering, long-run counter wrap and speed
telemetry were unverified at that session close. The 2026-07-29 sections above
supersede the modular-delta and production CPS telemetry items.

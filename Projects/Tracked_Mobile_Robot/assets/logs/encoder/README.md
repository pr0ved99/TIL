# Encoder Logs

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
- Overall encoder verification remains `PARTIAL` until wrap-safe delta, speed telemetry, vehicle left/right/forward sign and powered-motor noise are verified.

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
telemetry remain unverified.

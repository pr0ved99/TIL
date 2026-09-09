# Vehicle-Frame Encoder Mapping and Sign Verification

Date: `2026-07-30`

## Confirmed Physical Mapping

| Vehicle side | Bench motor | STM32 timer | Production TEL field |
| --- | --- | --- | --- |
| Right | Motor A | TIM5 / PA0, PA1 | `right_cps` |
| Left | Motor B | TIM3 / PB4, PB5 | `left_cps` |

## Forward-Positive Rule

The vehicle coordinate convention is:

```text
forward wheel/track motion -> positive CPS
reverse wheel/track motion -> negative CPS
```

With the installed motor orientation:

| Side | Physical forward viewed from output-shaft end | Raw timer sign | Production normalization |
| --- | --- | --- | --- |
| Right / Motor A / TIM5 | Clockwise | Positive | Keep raw sign |
| Left / Motor B / TIM3 | Counter-clockwise | Negative | Invert TIM3 sign |

Firmware normalization:

```c
uart_mvp_set_encoder_cps(
  encoder_cps_to_i32(-s_encoder_tim3.counts_per_second),
  encoder_cps_to_i32(s_encoder_tim5.counts_per_second)
);
```

USART2 `ENC3/ENC5` diagnostic rows intentionally retain raw timer signs. Only the production vehicle-frame `left_cps/right_cps` fields apply this normalization.

## Operator Verification

After the mapping change, the operator manually rotated each installed-side motor in its physical forward direction and confirmed that the corresponding normalized production CPS field became positive. The sign correction was reported as successful before proceeding to the fault-injection test.

Result: `PASS — encoder-side physical assignment and forward-positive production sign`

## Evidence Boundary

This record is reconstructed from the operator-controlled bench observation and source inspection; no new raw serial file was saved for this exact sign-normalization run. It does not verify the MDD10A powered channel 1/2 to physical left/right mapping, command-driven motor polarity, powered-motor noise, wheel linear speed, track travel, or closed-loop control.

Related earlier raw evidence:

- [`2026-07-29_dual_encoder_cps_tel_cw_pass.txt`](2026-07-29_dual_encoder_cps_tel_cw_pass.txt)
- [`2026-07-29_dual_encoder_cps_tel_ccw_pass.txt`](2026-07-29_dual_encoder_cps_tel_ccw_pass.txt)
- [`2026-07-29_dual_encoder_cps_uart_telemetry_verification.md`](2026-07-29_dual_encoder_cps_uart_telemetry_verification.md)

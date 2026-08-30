# Dual Encoder CPS UART Telemetry Verification

## Scope

- Date: 2026-07-29
- Path under test: encoder A/B -> STM32 TIM3/TIM5 -> `encoder_speed` -> STM32 production `TEL` -> ESP32 parser/log
- Motion source: output shaft hand rotation with the main DC switch on, the
  production motor-output hook disabled (`0U`), and no intentional motor drive
- Sample interval observed in `TEL`: 100 ms
- Bench sequence: motor A first, then motor B; the two motors were not moved simultaneously
- Vehicle left/right assignment: TBD

## Preserved Evidence

| Evidence | SHA-256 |
| --- | --- |
| [`2026-07-29_dual_encoder_cps_tel_stationary_clean_reset_pass.txt`](2026-07-29_dual_encoder_cps_tel_stationary_clean_reset_pass.txt) | `A60BDBC017596ED8F007963E1248992F15C8300A0E39410964BCD802447950A0` |
| [`2026-07-29_dual_encoder_cps_tel_cw_pass.txt`](2026-07-29_dual_encoder_cps_tel_cw_pass.txt) | `F8BCB1BBF749BB1E85DF9F634F0509A0D877E5B47A78503DA6FCC26332A0E998` |
| [`2026-07-29_dual_encoder_cps_tel_ccw_pass.txt`](2026-07-29_dual_encoder_cps_tel_ccw_pass.txt) | `7905171AC6C7D72204CA6B2088DAB7100C2B033DF249B353243E52ECB1C1DF3B` |

The reset capture begins with one cut fragment from the previous serial frame.
It is excluded from the complete-row assessment.

## Observed Mapping

| Bench motor | Timer input | Production TEL field | Clockwise | Counter-clockwise | Inactive field |
| --- | --- | --- | --- | --- | --- |
| A | TIM5, PA0/PA1 | `right_cps` | positive | negative | `left_cps=0` |
| B | TIM3, PB4/PB5 | `left_cps` | positive | negative | `right_cps=0` |

`left_cps` and `right_cps` are production protocol field names. The mapping is
provisional until the motors are physically installed and the vehicle left/right
and forward-positive conventions are confirmed.

## Results

### Clean reset and stationary

- STM32 restarted in `DISARMED`, `last_seq=0`.
- Both CPS fields remained zero.
- Complete telemetry rows continued at 100 ms intervals.
- The clean-reset portion began with `err=0`.

### Clockwise hand rotation

- 230 complete telemetry rows covered `t_ms=400..23300` with no 100 ms gap.
- Motor A produced only positive `right_cps`; 22 moving samples ranged from
  `+10` to `+580` CPS, with mean `+315.91` and median `+285` CPS.
- Motor B produced positive `left_cps`; the normal moving samples ranged from
  `+10` to `+390` CPS.
- A single `-10` sample occurred at a stop transition and did not persist.
- The inactive encoder field stayed at zero during each independent rotation.

### Counter-clockwise hand rotation

- 165 complete telemetry rows covered `t_ms=200..16600` with no 100 ms gap.
- Motor A produced 30 negative `right_cps` samples ranging from `-560` to
  `-10` CPS, with mean `-325` CPS. One `+20` stop/rebound sample did not persist.
- Motor B produced 29 negative `left_cps` samples ranging from `-760` to
  `-10` CPS, with mean `-484.14` and median `-550` CPS.
- The inactive encoder field stayed at zero during each independent rotation.

The later `err=2` value in the scripted captures is the accumulated result of
the intentional `NOT_ARMED` and `OUT_OF_RANGE` negative protocol cases. No new
parse, frame, or encoder movement error was observed.

## Decision

- STM32 dual wrap-safe CPS calculation: `PASS`
- Production `TEL` inclusion of both CPS fields: `PASS`
- ESP32 parsing and display of both CPS fields: `PASS`
- Independent channel isolation and stop-to-zero behavior: `PASS`
- Bench direction sign for both motors: `PASS`
- Vehicle left/right and forward-positive mapping: `NOT YET FIXED`
- Exact counts/rev and wheel-speed calibration: `NOT TESTED`
- Powered-motor noise and closed-loop speed control: `NOT TESTED`

This evidence closes the zero-output, manually rotated production CPS telemetry
subtest. It does not test active PWM/motor-current noise, authorize powered
motion, or establish physical wheel speed accuracy.

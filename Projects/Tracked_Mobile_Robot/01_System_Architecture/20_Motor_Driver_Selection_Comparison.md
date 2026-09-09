# Motor Driver Selection Comparison

## Purpose

This document records why the first drivetrain MVP moved from a BTS7960-style
dual-PWM plan to the MDD10A motor-driver path.

The goal is not to erase the BTS7960 exploration. The useful portfolio story is
the design change itself: what was considered, what changed, and how the change
affects wiring, firmware, and validation.

## Conclusion

The active first drivetrain path is MDD10A.

```text
Previous candidate: BTS7960 dual-PWM H-bridge module x2
Current decision:   MDD10A dual-channel PWM + DIR driver x1
```

BTS7960 remains as a superseded design alternative. It was a reasonable early
candidate, but MDD10A is better for the current first MVP because it reduces
board count, PWM-channel pressure, wiring complexity, and validation surface.

## Comparison

| Topic | BTS7960 path | MDD10A path | Project decision |
| --- | --- | --- | --- |
| Board count | One BTS7960 module per motor, two modules total | One MDD10A controls both left and right motors | MDD10A is simpler for bench bring-up |
| Control interface | `RPWM` + `LPWM` + enable per motor | `PWM` + `DIR` per motor | MDD10A needs fewer STM32 outputs |
| STM32 PWM demand | Four PWM outputs for two motors | Two PWM outputs plus two DIR GPIOs | MDD10A reduces timer allocation pressure |
| Direction safety | Keep inactive PWM zero and command only one PWM side | Ramp PWM to zero before changing DIR | Both need firmware safety rules |
| Enable behavior | Separate enable pins can be managed | No separate enable pin; PWM zero and power path are the basic shutoff | MDD10A may need an optional power gate later |
| Reset safety | Enable pull-downs should be validated | PWM safe default and optional pull-downs should be validated | Both need boot-safe tests |
| Logic compatibility | Actual module threshold must be verified | MDD10A supports 3.3 V / 5 V logic input | MDD10A has lower first-connection risk |
| Validation complexity | Two modules, enable logic, dual-PWM mutual exclusion | Two channels, PWM/DIR mapping, direction-change rule | MDD10A gets to no-load testing faster |
| Current status | Preserved as design history | Active first drivetrain decision | Use MDD10A |

## Why BTS7960 Was Considered

BTS7960 was a reasonable initial candidate.

- It is useful for learning H-bridge and dual-PWM motor control.
- One module per motor makes the left/right power stage physically separate.
- It has more practical current margin than a small TB6612FNG-class driver.
- It resembles the dual-PWM control structure found in local WHEELTEC reference
  code.

That history should remain in the project because it shows design exploration
instead of a magical final answer.

## Why MDD10A Was Selected

MDD10A better matches the first MVP.

1. One board handles both left and right DC motors.
2. STM32 only needs `PWM_L`, `DIR_L`, `PWM_R`, and `DIR_R`.
3. The existing candidate pin map can stay close to PB6/PB7 PWM and PC8/PC9 DIR.
4. Firmware does not need BTS7960-style `RPWM`/`LPWM` mutual exclusion.
5. MDD10A supports direct 3.3 V logic-level control from the NUCLEO-F446RE.
6. The validation path becomes clearer: visual/DMM check, power bring-up,
   PWM/DIR logic test, then no-load motor test.

## Firmware Impact

The BTS7960 path would have exposed outputs like this:

```text
left_rpwm
left_lpwm
right_rpwm
right_lpwm
left_enable
right_enable
```

The MDD10A path uses this canonical output shape:

```text
left_pwm
left_dir
right_pwm
right_dir
```

The high-level motor abstraction stays the same:

- signed motor command
- output permission
- command timeout
- PWM clamp
- ramp limit
- encoder sign validation
- low-voltage stop

Only the low-level output mapping changes:

```text
signed command > 0  -> PWM = duty, DIR = forward mapping
signed command < 0  -> PWM = duty, DIR = reverse mapping
signed command == 0 -> PWM = 0
unsafe state        -> PWM = 0
```

Direction changes must follow this rule:

```text
if direction must change:
    ramp PWM to 0
    change DIR
    apply limited PWM
```

## Wiring Impact

Current first wiring contract:

```text
STM32 PB6 / TIM4_CH1 -> MDD10A PWM1
STM32 PC8            -> MDD10A DIR1
STM32 PB7 / TIM4_CH2 -> MDD10A PWM2
STM32 PC9            -> MDD10A DIR2
STM32 GND            -> MDD10A GND

3S LiPo + -> fuse -> switch -> MDD10A POWER+
3S LiPo - ------------------> MDD10A POWER-

Output channel 1 -> MDD10A M1A/M1B -> physical side TBD
Output channel 2 -> MDD10A M2A/M2B -> physical side TBD
```

The MCU-to-driver routing has passed static/no-motor bench checks. The final
powered channel 1/2 to physical left/right mapping still requires a motor
direction test; the encoder-side sign result alone does not close it.

## Validation Impact

The active hardware validation order is:

1. `00_MDD10A_Visual_and_Multimeter_Inspection.md`
2. `01_Power_Bringup_Checklist.md`
3. `02_Buck_Converter_Calibration_Log.md`
4. `03_MDD10A_Logic_Input_Test.md`
5. `04_Encoder_Signal_Safety_Test.md`
6. `05_First_Motor_No_Load_Test.md`
7. `06_Left_Right_Drivetrain_Test.md`

BTS7960-specific logic validation is no longer the active first-driver path.

## Decision Record

| Date | Decision | Reason |
| --- | --- | --- |
| Before 2026-06-04 | Consider BTS7960-class dual-PWM path | Natural fit with H-bridge learning and WHEELTEC dual-PWM references |
| 2026-06-08 | Move first drivetrain path to MDD10A | Available part, integrated dual channel, lower STM32 pin pressure, 3.3 V logic support, simpler validation |
| Current | Preserve BTS7960 as superseded alternative | Useful comparison point and design-evolution evidence |

## Final Rule

Use MDD10A whenever a document describes the active motor-driver path.

Use BTS7960 only for:

- historical decision context
- driver-option comparison
- explaining why MDD10A was selected
- a future reconsideration if measured MDD10A current or heat margin is not
  enough

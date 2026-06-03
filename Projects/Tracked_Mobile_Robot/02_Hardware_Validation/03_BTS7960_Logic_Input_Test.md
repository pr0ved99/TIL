# BTS7960 Logic Input Test

## 목적

이 문서는 BTS7960 motor driver를 motor power 없이 logic input 중심으로 먼저 검증하는 절차를 정의한다.

목표는 STM32가 `RPWM`, `LPWM`, `R_EN`, `L_EN`을 안전하게 제어할 수 있는지 확인하고, firmware boot/reset 중 motor가 의도치 않게 enable되지 않도록 검증하는 것이다.

## Test Scope

이 단계에서 허용:

- BTS7960 logic supply 연결
- STM32 PWM/GPIO signal 연결
- Common GND 연결
- PWM duty zero 확인
- Enable default disabled 확인
- `RPWM`/`LPWM` 동시 active 금지 확인

이 단계에서 금지:

- Motor output에 motor 연결
- BTS7960 B+ motor power를 본격적으로 사용
- Track을 지면에 둔 상태로 motor 구동
- Enable을 항상 high로 묶어두기

## Required Signals

각 motor driver module:

| BTS7960 pin | STM32 role | Expected behavior |
| --- | --- | --- |
| `RPWM` | PWM output | Positive command side |
| `LPWM` | PWM output | Negative command side |
| `R_EN` | GPIO enable | Disabled during boot/reset |
| `L_EN` | GPIO enable | Disabled during boot/reset |
| `VCC` | Logic supply | Module requirement 확인 |
| `GND` | Common ground | STM32 GND와 common |

## Pre-Test Checks

| Check | Expected | Result |
| --- | --- | --- |
| BTS7960 module pinout identified | Yes | TBD |
| Logic supply voltage requirement checked | Yes | TBD |
| STM32 GPIO logic level compatibility checked | 3.3 V accepted or level shifting planned | TBD |
| STM32 GND and BTS7960 GND common | Yes | TBD |
| Motor power disconnected | Yes | TBD |
| Motor output disconnected | Yes | TBD |
| Enable pull-down plan exists | Yes | TBD |

## Firmware Safety Expectations

Boot default:

```text
RPWM = 0
LPWM = 0
R_EN = 0
L_EN = 0
state = SAFETY_BOOT -> SAFETY_DISARMED
```

Allowed command mapping:

| State | RPWM | LPWM | Enable |
| --- | --- | --- | --- |
| Boot/disarmed/fault | 0 | 0 | 0 |
| Armed idle | 0 | 0 | 1 or test-defined |
| Forward test | low duty | 0 | 1 |
| Reverse test | 0 | low duty | 1 |
| Forbidden | duty | duty | never |

## Test 1: Boot Output State

Procedure:

1. Connect STM32 to PC through USB only.
2. Keep BTS7960 motor power disconnected.
3. Flash firmware or run GPIO/PWM test firmware.
4. Measure or observe `RPWM`, `LPWM`, `R_EN`, `L_EN`.

Expected:

- PWM channels are zero.
- Enable lines are disabled.
- No pin floats into an unsafe enable state.

| Signal | Expected | Measured/observed | Result |
| --- | --- | --- | --- |
| Left RPWM | 0 | TBD | TBD |
| Left LPWM | 0 | TBD | TBD |
| Left enable | 0 | TBD | TBD |
| Right RPWM | 0 | TBD | TBD |
| Right LPWM | 0 | TBD | TBD |
| Right enable | 0 | TBD | TBD |

## Test 2: Enable Control

Procedure:

1. Keep PWM zero.
2. Toggle enable GPIO through firmware command or test sequence.
3. Observe enable pins.
4. Confirm disarm and E-stop force enable low.

| Driver | Enable low observed | Enable high observed | Disarm forces low | E-stop forces low |
| --- | --- | --- | --- | --- |
| Left BTS7960 | TBD | TBD | TBD | TBD |
| Right BTS7960 | TBD | TBD | TBD | TBD |

## Test 3: Dual-PWM Mutual Exclusion

Procedure:

1. Send or simulate positive command.
2. Confirm only `RPWM` is active.
3. Send or simulate negative command.
4. Confirm only `LPWM` is active.
5. Send zero command.
6. Confirm both PWM channels are zero.

| Driver | Positive command | Negative command | Zero command | Result |
| --- | --- | --- | --- | --- |
| Left BTS7960 | TBD | TBD | TBD | TBD |
| Right BTS7960 | TBD | TBD | TBD | TBD |

Pass condition:

```text
RPWM and LPWM are never active at the same time.
```

## Test 4: Command Timeout Output

Procedure:

1. Enter armed test state if implemented.
2. Apply low-duty test command.
3. Stop sending command.
4. Confirm timeout sets PWM zero and disables or idles enable according to state machine.

| Item | Expected | Observed |
| --- | --- | --- |
| Command age exceeds timeout | Yes | TBD |
| PWM after timeout | 0 | TBD |
| Enable after timeout | Disabled or safe idle | TBD |
| Fault/state telemetry | Timeout state | TBD |

## Stop Conditions

Stop if:

- Enable is high during boot unexpectedly
- `RPWM` and `LPWM` are active together
- Logic input voltage exceeds safe range
- BTS7960 heats without motor power
- STM32 resets when logic input is connected
- Signal wiring or ground is uncertain

## Result Summary

| Item | Pass/Fail | Notes |
| --- | --- | --- |
| Boot output safe | TBD | TBD |
| Enable control safe | TBD | TBD |
| Dual-PWM mutual exclusion | TBD | TBD |
| Timeout output safe | TBD | TBD |
| Ready for motor power test | TBD | TBD |

## Next Step

BTS7960 logic input이 안전하게 검증되면 encoder signal을 먼저 확인하거나, motor 1개 무부하 테스트로 넘어간다.

```text
04_Encoder_Signal_Safety_Test.md
05_First_Motor_No_Load_Test.md
```

# MDD10A Logic Input Test

## 목적

이 문서는 MDD10A motor driver를 motor power 없이 logic input 중심으로 먼저 검증하는 절차를 정의한다.

목표는 STM32가 `PWM1`, `DIR1`, `PWM2`, `DIR2`를 안전하게 제어할 수 있는지 확인하고,
firmware boot/reset 중 motor가 의도치 않게 구동되지 않도록 검증하는 것이다.

## Test Scope

이 단계에서 허용되는 것:

- STM32 PWM/DIR 출력 측정
- MDD10A logic GND와 STM32 GND 공통 연결
- MDD10A POWER disconnected 상태의 STM32 signal-only 확인
- MDD10A POWER connected, motor disconnected 상태의 짧은 no-motor driver check
- Low duty PWM waveform 확인
- Direction command에 따른 DIR state 확인

이 단계에서 금지되는 것:

- MDD10A POWER+에 motor battery 연결
- Motor output terminal에 실제 motor 연결
- High duty test
- PWM이 0이 아닌 상태에서 direction을 바꾸는 firmware sequence

## Signal Contract

MDD10A sign-magnitude 기준:

| MDD10A pin | STM32 role | Expected behavior |
| --- | --- | --- |
| `PWM1` | Left motor PWM candidate | Motor 1 speed duty |
| `DIR1` | Left motor direction candidate | Motor 1 direction |
| `PWM2` | Right motor PWM candidate | Motor 2 speed duty |
| `DIR2` | Right motor direction candidate | Motor 2 direction |
| `GND` | Common reference | STM32 GND와 공통 |

초기 channel mapping은 bench 결과로 확정한다.

```text
PWM1/DIR1 -> left motor candidate
PWM2/DIR2 -> right motor candidate
```

주의:

```text
MDD10A에는 BTS7960식 별도 logic VCC pin이 없다.
따라서 첫 단계는 STM32가 connector 쪽으로 내보내는 PWM/DIR signal을 확인하는 signal-only test이고,
MDD10A board 자체를 켠 상태의 확인은 POWER 입력을 fuse/switch를 통해 연결하되 motor는 분리한 상태에서 짧게 수행한다.
```

## Required Preconditions

| Precondition | Required | Result |
| --- | --- | --- |
| STM32 firmware can set PWM duty to zero | Yes | TBD |
| STM32 firmware can toggle DIR GPIO | Yes | TBD |
| MDD10A terminal label identified | Yes | TBD |
| STM32 GND and MDD10A GND common | Yes | TBD |
| Signal-only test: MDD10A POWER disconnected | Yes | TBD |
| Driver-powered no-motor test: motor disconnected | Yes | TBD |
| Motor disconnected | Yes | TBD |

## Safe Boot State

Required boot state:

```text
PWM1 = 0
PWM2 = 0
DIR1 = defined default or don't care
DIR2 = defined default or don't care
```

Important rule:

```text
DIR state alone must not create motor output. PWM must be zero until safety gate allows motion.
```

## Test 1: Boot/Reset Logic State

Procedure:

1. Keep MDD10A POWER disconnected for signal-only test.
2. Connect STM32 GND to MDD10A GND.
3. Boot or reset STM32.
4. Measure or observe `PWM1`, `PWM2`, `DIR1`, `DIR2`.

Pass condition:

- `PWM1` and `PWM2` remain zero.
- DIR pins do not matter while PWM is zero, but their default state is recorded.
- No pin floats into an unsafe or unknown PWM-active state.

| Signal | Expected | Observed | Result |
| --- | --- | --- | --- |
| `PWM1` | 0 | TBD | TBD |
| `PWM2` | 0 | TBD | TBD |
| `DIR1` | recorded | TBD | TBD |
| `DIR2` | recorded | TBD | TBD |

## Test 2: Low-Duty PWM Output

Procedure:

1. Keep motor power disconnected.
2. Command low duty on `PWM1`.
3. Return `PWM1` to zero.
4. Command low duty on `PWM2`.
5. Return `PWM2` to zero.

| Channel | Expected duty | Observed waveform | Result |
| --- | --- | --- | --- |
| `PWM1` | 5-10% candidate | TBD | TBD |
| `PWM2` | 5-10% candidate | TBD | TBD |

Pass condition:

```text
PWM frequency and duty match firmware configuration, and both channels return to zero.
```

## Test 3: Direction GPIO Behavior

Procedure:

1. Keep `PWM1` and `PWM2` at zero.
2. Toggle `DIR1`.
3. Toggle `DIR2`.
4. Record logic levels for forward and reverse mapping candidates.

| Channel | Forward DIR level | Reverse DIR level | Result |
| --- | --- | --- | --- |
| Motor 1 | TBD | TBD | TBD |
| Motor 2 | TBD | TBD | TBD |

Pass condition:

```text
DIR changes are deterministic, and firmware never changes DIR while PWM is nonzero.
```

## Test 4: Direction-Change Safety Sequence

Procedure:

1. Apply low duty PWM to one channel in a logic-only test.
2. Request reverse command.
3. Confirm firmware first sets PWM to zero.
4. Confirm DIR changes only after PWM zero.
5. Confirm PWM is applied again only after DIR is stable.

| Step | Expected | Observed |
| --- | --- | --- |
| Forward PWM active | Low duty | TBD |
| Reverse requested | PWM goes zero first | TBD |
| DIR changes | After PWM zero | TBD |
| Reverse PWM active | Low duty after DIR stable | TBD |

## Test 5: Timeout/Disarm Logic

Procedure:

1. Apply logic-only low duty command.
2. Trigger command timeout or `DISARM`.
3. Confirm both PWM channels go zero.

| Event | Expected | Observed |
| --- | --- | --- |
| Command timeout | `PWM1=0`, `PWM2=0` | TBD |
| DISARM | `PWM1=0`, `PWM2=0` | TBD |
| E-stop if implemented | `PWM1=0`, `PWM2=0` | TBD |

## Stop Conditions

Stop test immediately if:

- Any PWM channel is active at boot/reset
- PWM does not return to zero after command stop
- DIR changes while PWM is nonzero
- Logic wiring becomes hot
- MDD10A heats during powered no-motor check
- Signal polarity or terminal identity is uncertain

## Result Summary

| Item | Pass/Fail | Notes |
| --- | --- | --- |
| Boot PWM zero | TBD | TBD |
| PWM1 waveform | TBD | TBD |
| PWM2 waveform | TBD | TBD |
| DIR1 behavior | TBD | TBD |
| DIR2 behavior | TBD | TBD |
| Direction-change sequence | TBD | TBD |
| Timeout/disarm PWM zero | TBD | TBD |

## Next Step

MDD10A logic input이 안전하게 검증되면 encoder signal을 먼저 확인하거나, motor 1개 무부하 테스트로 넘어간다.

```text
04_Encoder_Signal_Safety_Test.md
05_First_Motor_No_Load_Test.md
```

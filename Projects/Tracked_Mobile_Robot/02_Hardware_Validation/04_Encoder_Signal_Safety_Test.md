# Encoder Signal Safety Test

## 목적

이 문서는 motor encoder를 STM32에 연결하기 전에 전압, ground, signal behavior를 검증하는 절차를 정의한다.

이전 Jetson 테스트에서 5 V rail이 약 2.1 V로 떨어진 현상이 있었으므로, encoder를 STM32에 바로 연결하지 않고 단독 전원 및 신호 확인을 먼저 진행한다.

## Core Rule

핵심 규칙:

```text
Encoder output voltage를 측정하기 전에는 STM32 pin에 연결하지 않는다.
```

STM32 input은 3.3 V logic이 기본이다. 일부 pin은 5 V tolerant일 수 있지만, 모든 상황에서 안전하다고 가정하지 않는다. 특히 analog mode, internal pull-up/down, unpowered board 상태에서는 더 조심해야 한다.

## Test Scope

이 단계에서 확인:

- Encoder power input voltage
- Encoder current draw estimate
- A/B output idle voltage
- A/B output high voltage
- Output type 추정: push-pull, open-collector/open-drain 가능성
- Common ground
- Level shifter 또는 resistor divider 필요 여부
- Encoder direction sign

## Required Equipment

| Item | Purpose |
| --- | --- |
| Multimeter | Voltage and continuity check |
| Optional oscilloscope/logic analyzer | A/B pulse observation |
| Safe 5 V supply | Encoder power test |
| Current-limited supply if available | Overcurrent protection |
| Level shifter or resistor divider parts | STM32 input protection if needed |
| Pull-up resistor candidates | Open-collector/open-drain test |

## Encoder Identification

| Motor | Encoder status | Connector wires identified | Notes |
| --- | --- | --- | --- |
| MG540 left | TBD | TBD | TBD |
| MG540 right | TBD | TBD | TBD |
| JGB37-520 left | Encoder may be faulty | TBD | TBD |
| JGB37-520 right | Encoder may be faulty | TBD | TBD |

Wire map:

| Wire color | Candidate function | Verified? |
| --- | --- | --- |
| TBD | Vcc | TBD |
| TBD | GND | TBD |
| TBD | Encoder A | TBD |
| TBD | Encoder B | TBD |
| TBD | Optional index or motor lead | TBD |

## Test 1: Resistance and Short Check

Power disconnected 상태에서 측정한다.

| Check | Expected | Result |
| --- | --- | --- |
| Vcc to GND resistance | Not short | TBD |
| A to GND resistance | Not short | TBD |
| B to GND resistance | Not short | TBD |
| A to B resistance | Not short | TBD |
| Connector polarity marked | Yes | TBD |

## Test 2: Encoder Power Test Without STM32

Procedure:

1. Encoder를 STM32와 분리한다.
2. Safe 5 V supply 또는 current-limited supply를 사용한다.
3. Encoder Vcc/GND만 연결한다.
4. Supply voltage sag를 측정한다.
5. Heat 또는 smell을 확인한다.

| Motor | Supply voltage before | Supply voltage connected | Heat/smell | Result |
| --- | --- | --- | --- | --- |
| Motor 1 | TBD | TBD | TBD | TBD |
| Motor 2 | TBD | TBD | TBD | TBD |

Stop if:

- 5 V가 크게 sag한다.
- Encoder가 뜨거워진다.
- Vcc/GND polarity가 불확실하다.
- 전류 제한 supply가 current limit에 걸린다.

## Test 3: A/B Output Voltage

Procedure:

1. Encoder에만 전원을 공급한다.
2. Motor shaft를 천천히 손으로 돌린다.
3. A와 B voltage를 GND 기준으로 측정한다.
4. 가능하면 oscilloscope 또는 logic analyzer로 pulse를 본다.

| Motor | A low | A high | B low | B high | Output safe for STM32? |
| --- | --- | --- | --- | --- | --- |
| Motor 1 | TBD | TBD | TBD | TBD | TBD |
| Motor 2 | TBD | TBD | TBD | TBD | TBD |

Decision:

| Condition | Action |
| --- | --- |
| A/B high <= 3.3 V | STM32 input candidate 가능 |
| A/B high near 5 V | Level shifter 또는 divider 필요 |
| A/B floating | Pull-up 필요 가능성 |
| A/B no pulse | Encoder wiring 또는 encoder fault 조사 |

## Test 4: Pull-up and Output Type Check

Open-collector/open-drain encoder일 가능성이 있으면 pull-up이 필요할 수 있다.

Procedure:

1. A/B output이 floating인지 확인한다.
2. Module 내 pull-up 유무를 추정한다.
3. 3.3 V pull-up으로 동작 가능한지 확인한다.
4. 5 V pull-up이 필요한 구조라면 level shifting을 설계한다.

| Motor | Pull-up needed? | Pull-up voltage | Pulse observed | Result |
| --- | --- | --- | --- | --- |
| Motor 1 | TBD | TBD | TBD | TBD |
| Motor 2 | TBD | TBD | TBD | TBD |

## Test 5: STM32 Protection Decision

| Signal | Measured high | STM32 direct? | Protection required | Decision |
| --- | --- | --- | --- | --- |
| Left A | TBD | TBD | TBD | TBD |
| Left B | TBD | TBD | TBD | TBD |
| Right A | TBD | TBD | TBD | TBD |
| Right B | TBD | TBD | TBD | TBD |

Protection options:

- Logic level shifter
- Resistor divider
- Series resistor plus clamp strategy only if designed carefully
- 3.3 V pull-up if encoder output is open-collector/open-drain

Initial recommendation:

```text
5 V encoder output이면 level shifter를 사용한다.
```

## Test 6: Direction Sign Test

STM32 연결 이후, track을 들어 올린 상태에서만 진행한다.

Procedure:

1. Timer encoder mode를 활성화한다.
2. Motor를 손으로 forward 방향으로 돌린다.
3. Count 증가/감소를 확인한다.
4. Low-duty forward command에서 left/right count sign을 확인한다.

| Motor | Manual forward sign | Powered forward sign | Needs sign inversion? |
| --- | --- | --- | --- |
| Left | TBD | TBD | TBD |
| Right | TBD | TBD | TBD |

Pass condition:

```text
Forward command에서 left/right encoder count convention이 문서와 일치한다.
```

## Stop Conditions

Stop immediately if:

- Encoder supply voltage collapses
- Encoder output exceeds STM32-safe voltage
- STM32 resets when encoder is connected
- A/B signal is shorted to motor power
- Signal behavior is unknown but motor power is being applied

## Result Summary

| Item | Pass/Fail | Notes |
| --- | --- | --- |
| Encoder power safe | TBD | TBD |
| A/B voltage measured | TBD | TBD |
| STM32 protection selected | TBD | TBD |
| Pulse observed | TBD | TBD |
| Direction sign known | TBD | TBD |
| Ready for encoder integration | TBD | TBD |

## Next Step

Encoder signal이 STM32-safe임을 확인한 뒤 motor no-load test와 encoder count logging을 연결한다.

```text
05_First_Motor_No_Load_Test.md
```

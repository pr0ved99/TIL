# Encoder Signal Safety Test

## 목적

이 문서는 MG540P30_12V motor encoder를 STM32에 연결하기 전에 전원, A/B 신호 전압과 입력 보호 조건을 검증한 기록이다.

2026-07-26 시험은 motor를 구동하지 않고 shaft를 손으로 돌리며 DMM으로 수행했다. Oscilloscope 또는 logic analyzer는 사용하지 않았다.

## Core Rule

```text
Raw encoder output을 STM32에 직접 연결하지 않는다.
각 A/B 신호에 15 kΩ signal-to-GND load를 유지한 상태에서만
제한적인 STM32 hand-rotation count 시험으로 진행한다.
```

STM32의 일부 핀은 5 V tolerant이지만, unpowered board, power sequencing과 motor-noise 조건까지 안전하다고 가정하지 않는다.

## 측정값 표기 규칙

- `회전 평균`: shaft를 돌리는 동안 DMM에 표시된 평균 전압이다. Logic LOW 전압이 아니다.
- `정지 HIGH`: shaft를 HIGH 상태에 정지시킨 뒤 측정한 전압이다.
- 정지 상태는 shaft 위치에 따라 약 0 V 또는 HIGH가 될 수 있다.
- 실제 LOW 전압, pulse shape, A/B phase와 CPR은 별도로 계측하지 않았다.
- `MG540-A`, `MG540-B`는 bench 식별명이다. 차량 left/right는 아직 확정하지 않는다.

## Encoder Identification

| Bench ID | Model | Encoder status | Vehicle side | Notes |
| --- | --- | --- | --- | --- |
| MG540-A | WHEELTEC `MG540P30_12V` | Loaded-voltage gate conditional PASS | TBD | 첫 번째 측정 motor |
| MG540-B | WHEELTEC `MG540P30_12V` | Loaded-voltage gate conditional PASS | TBD | 두 번째 측정 motor |
| JGB37-520 candidates | TBD | Previous fault suspicion | TBD | 이번 시험 범위에서 제외 |

PCB의 자석/실크 면을 정면으로 보고 connector가 위쪽일 때, connector pad의 왼쪽부터 오른쪽 순서는 다음과 같다.

| Pad | Function | Verification |
| ---: | --- | --- |
| 1 | Motor `+` | PCB silkscreen/photo |
| 2 | Encoder GND | PCB silkscreen/photo |
| 3 | Encoder B | PCB silkscreen/photo |
| 4 | Encoder A | PCB silkscreen/photo |
| 5 | Encoder 5 V | PCB silkscreen/photo |
| 6 | Motor `-` | PCB silkscreen/photo |

Evidence:

- [`../assets/photos/encoder/2026-07-26_01_mg540_encoder_pcb_pinout.jpg`](../assets/photos/encoder/2026-07-26_01_mg540_encoder_pcb_pinout.jpg)
- [`../assets/photos/encoder/2026-07-26_02_mg540p30_12v_motor_label.jpg`](../assets/photos/encoder/2026-07-26_02_mg540p30_12v_motor_label.jpg)

## Test 1: Resistance and Short Check

전원을 모두 분리한 상태에서 측정했다.

| Motor | Check | Result | Decision |
| --- | --- | ---: | --- |
| MG540-A | Encoder 5 V to GND | 824 Ω | 0 Ω급 hard short 아님 |
| MG540-A | A to GND | DMM `1` / OL | Hard short 관찰 안 됨 |
| MG540-A | B to GND | DMM `1` / OL | Hard short 관찰 안 됨 |
| MG540-A | A to B | DMM `1` / OL | Hard short 관찰 안 됨 |
| MG540-A | Connector polarity | Photo/silkscreen으로 식별 | PASS |
| MG540-B | Resistance checks | 미기록 | TBD |

`824 Ω`은 hard short가 아니라는 최소 확인에만 사용한다. 이 값으로 encoder 소비전류를 계산하지 않는다.

## Test 2: Encoder Power Test Without STM32

XL4015 #2의 5 V rail을 사용하고 STM32 신호 입력은 연결하지 않았다.

| Motor | Supply before | Supply connected | Change | Heat/smell/current | Result |
| --- | ---: | ---: | ---: | --- | --- |
| MG540-A | 5.06 V | 5.03 V | -0.03 V | 미기록 | Voltage stability PASS |
| MG540-B | 미기록 | 5.03 V | 계산 불가 | 미기록 | Connected voltage nominal; sag 판정 TBD |

## Test 3: A/B Output Voltage

### Raw observation

- 별도 signal-to-GND 저항을 달기 전 MG540-A에서 A/B가 shaft 위치에 따라 약 0 V 또는 약 5 V가 되는 것을 확인했다.
- 손으로 계속 돌릴 때 DMM에는 A `0.01~2.48 V`, B `2.48~4.98 V` 범위가 보였다.
- 이 범위는 slow DMM sampling이 pulse를 평균 낸 관찰값이며, LOW/HIGH timing 또는 A/B 위상을 입증하지 않는다.
- Raw 5 V 계열 신호는 STM32에 직접 연결하지 않는다.

### Loaded measurement

각 측정은 해당 A 또는 B signal과 encoder GND 사이에 저항 하나를 연결해 수행했다.

| Motor | Signal load | A 회전 평균 | A 정지 HIGH | B 회전 평균 | B 정지 HIGH | 정확한 LOW |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| MG540-A | 10 kΩ | 1.23 V | 2.48 V | 1.24 V | 2.48 V | 미기록 |
| MG540-A | 15 kΩ | 1.48 V | 2.98 V | A상과 거의 동일 | A상과 거의 동일 | 미기록 |
| MG540-B | 15 kΩ | 1.46 V | 2.97 V | 1.47 V | 2.96 V | 미기록 |

MG540-A의 15 kΩ B상은 동등한 동작만 확인했고 정확한 숫자를 따로 기록하지 않았으므로 A상 값을 복사하지 않는다.

## Test 4: Output-Type Inference

PCB의 R1/R2에는 `103` marking이 보여 nominal 10 kΩ 저항으로 보인다. 또한 5.03 V rail과 loaded HIGH를 단순 저항 분배로 역산하면 등가 상단 저항이 약 10.3~10.5 kΩ이다.

```text
R_internal = R_load * (V_supply / V_high - 1)
```

| Measurement | Calculated equivalent upper resistance |
| --- | ---: |
| MG540-A, 10 kΩ load, 2.48 V HIGH | 10.28 kΩ |
| MG540-A, 15 kΩ load, 2.98 V HIGH | 10.32 kΩ |
| MG540-B A, 15 kΩ load, 2.97 V HIGH | 10.40 kΩ |
| MG540-B B, 15 kΩ load, 2.96 V HIGH | 10.49 kΩ |

판정:

```text
측정 결과는 약 10 kΩ internal pull-up이 5 V rail에 연결된 구조와 강하게 일치한다.
그러나 이 측정만으로 open-collector/open-drain 회로형식을 확정하지는 않는다.
```

## Test 5: STM32 Protection Decision

15 kΩ signal-to-GND load는 기록된 채널에서 HIGH를 2.96~2.98 V로 만들었고, 10 kΩ보다 STM32 HIGH margin이 크면서 3.3 V 아래를 유지했다.

| Bench signal | Raw direct | With 15 kΩ load | Decision |
| --- | --- | ---: | --- |
| MG540-A A | 금지 | 2.98 V HIGH | Voltage gate PASS |
| MG540-A B | 금지 | A상과 거의 동일, exact value 미기록 | Conditional PASS; 수치 재기록 권장 |
| MG540-B A | 금지 | 2.97 V HIGH | Voltage gate PASS |
| MG540-B B | 금지 | 2.96 V HIGH | Voltage gate PASS |

첫 STM32 hand-rotation 시험의 임시 연결 조건:

```text
Encoder A ----+---- 15 kΩ ---- GND
              +---- 330 Ω~1 kΩ series 후보 ---- STM32 timer input

Encoder B ----+---- 15 kΩ ---- GND
              +---- 330 Ω~1 kΩ series 후보 ---- STM32 timer input

Encoder GND ------------------------------- STM32 GND
```

- 15 kΩ load는 A/B 각각 하나씩 필요하다.
- Common GND가 필수다.
- 330 Ω~1 kΩ series 저항의 최종 값과 실제 배선은 아직 검증하지 않았다.
- 첫 timer 입력 후보는 `PB4/TIM3_CH1`, `PB5/TIM3_CH2`다.
- 두 번째 후보는 `PA0/TIM5_CH1`, `PA1/TIM5_CH2`다.
- 이 단계에서는 motor power를 넣지 않고 shaft를 손으로만 돌린다.

## Test 6: Direction Sign and Count

| Bench motor | Timer candidate | Manual count | Direction sign | Vehicle side |
| --- | --- | --- | --- | --- |
| MG540-A 또는 MG540-B 중 첫 연결 motor | TIM3 PB4/PB5 | TBD | TBD | TBD |
| 나머지 motor | TIM5 PA0/PA1 | TBD | TBD | TBD |

MG540-A/B를 left/right로 부르지 않는다. 실제 장착 방향과 forward 기준이 정해진 뒤 channel assignment와 sign inversion을 확정한다.

## Stop Conditions

- Encoder rail이 크게 sag하거나 encoder가 뜨거워진다.
- 15 kΩ load 상태의 A/B HIGH가 3.3 V를 넘는다.
- STM32가 encoder 연결 시 reset된다.
- A/B가 motor power와 short된 것으로 의심된다.
- Motor power가 연결된 상태에서 signal behavior를 처음 확인하려 한다.

## Result Summary

| Item | Result | Notes |
| --- | --- | --- |
| Encoder rail | `CONDITIONAL PASS` | MG540-A 5.06 -> 5.03 V, MG540-B connected 5.03 V; current/heat 미기록 |
| Raw A/B behavior | `OBSERVED` | Shaft 위치에 따라 약 0/5 V; direct STM32 connection 금지 |
| 15 kΩ loaded HIGH | `CONDITIONAL PASS` | Exact-recorded channels 2.96~2.98 V |
| Output structure | `PROBABLE` | 약 10 kΩ internal 5 V pull-up과 일치하지만 회로형식 미확정 |
| DMM state-change observation | `OBSERVED / PULSE NOT VERIFIED` | DMM 평균 변화만 확인; LOW, pulse shape와 phase 미계측 |
| STM32 input protection | `SELECTED / NOT FULLY INTEGRATED` | 채널별 15 kΩ load; series resistor는 후보 |
| Direction sign and count | `NOT TESTED` | TIM encoder-mode 시험 필요 |
| Limited hand-rotation STM32 test | `READY WITH CONDITIONS` | 15 kΩ per channel, common GND, motor power disconnected |
| Powered closed-loop operation | `NOT READY` | Count/sign, active motor safety와 no-load 시험 필요 |

## Next Step

1. 현재 firmware/CubeMX 상태를 Git 기준점으로 보존한다.
2. TIM3의 `PB4/PB5`를 첫 encoder input 후보로 설정한다.
3. A/B 각각에 15 kΩ load와 입력 series resistor를 적용하고 motor power 없이 손회전 count만 확인한다.
4. Count가 안정되면 TIM5 `PA0/PA1`로 두 번째 channel을 반복한다.
5. 실제 motor no-load 시험은 active timeout/DISARM output-zero gate까지 통과한 뒤 진행한다.

관련 절차: [`05_First_Motor_No_Load_Test.md`](05_First_Motor_No_Load_Test.md)

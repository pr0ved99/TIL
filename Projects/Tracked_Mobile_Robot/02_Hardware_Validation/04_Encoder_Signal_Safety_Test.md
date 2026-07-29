# Encoder Signal Safety Test

## 목적

이 문서는 MG540P30_12V motor encoder를 STM32에 연결하기 전에 전원, A/B 신호 전압과 입력 보호 조건을 검증한 기록이다.

2026-07-26 시험은 motor를 구동하지 않고 shaft를 손으로 돌리며 DMM으로 수행했다.
2026-07-27에는 같은 signal-conditioning 조건에서 TIM3와 TIM5에 encoder 두 개를
동시에 연결하고 독립 count/sign을 USART raw log로 확인했다. Oscilloscope 또는
logic analyzer는 사용하지 않았다.
2026-07-29에는 main DC switch를 켜되 production motor-output hook은 `0U`로
비활성화하고 의도적인 motor 구동 없이 각 shaft를 독립적으로 시계·반시계 방향으로
손회전했다. STM32 production `TEL`의 signed CPS와 ESP32 structured parser까지
end-to-end로 확인했으며 active PWM/motor-current noise 시험은 아니다.
2026-07-30에는 출력축을 motor별·방향별 50회전시켜 `1560 counts/output rev`를
firmware 변환 상수로 확정하고, signed CPS -> mRPM self-test와 dual hand-rotation
동적 계산 일치를 확인했다.

## Core Rule

```text
Raw encoder output을 STM32에 직접 연결하지 않는다.
각 A/B 신호는 1 kΩ series resistor를 지난 STM32 input node에서
15 kΩ으로 common GND에 pull-down한 상태에서만 연결한다.
```

STM32의 일부 핀은 5 V tolerant이지만, unpowered board, power sequencing과 motor-noise 조건까지 안전하다고 가정하지 않는다.

## 측정값 표기 규칙

- `회전 평균`: shaft를 돌리는 동안 DMM에 표시된 평균 전압이다. Logic LOW 전압이 아니다.
- `정지 HIGH`: shaft를 HIGH 상태에 정지시킨 뒤 측정한 전압이다.
- 정지 상태는 shaft 위치에 따라 약 0 V 또는 HIGH가 될 수 있다.
- 정확한 LOW 전압과 pulse shape는 별도 계측하지 않았다.
- A/B quadrature 동작, count sign과 출력축 1회전 count는 TIM3 손회전 시험으로 기능 확인했다.
- `MG540-A`, `MG540-B`는 bench 식별명이다. 차량 left/right는 아직 확정하지 않는다.

## Encoder Identification

| Bench ID | Model | Encoder status | Vehicle side | Notes |
| --- | --- | --- | --- | --- |
| MG540-A | WHEELTEC `MG540P30_12V` | TIM3 sequential PASS; dual-session included | TBD | 2026-07-27 raw log mapping은 미기록; 2026-07-29 operator sequence에서 TIM5/`right_cps`로 확인 |
| MG540-B | WHEELTEC `MG540P30_12V` | TIM3 sequential PASS; dual-session included | TBD | 2026-07-27 raw log mapping은 미기록; 2026-07-29 operator sequence에서 TIM3/`left_cps`로 확인 |
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

최종적으로 사용한 STM32 hand-rotation 시험 연결 조건:

```text
Encoder A ---- 1 kΩ ----+---- STM32 timer input
                        |
                       15 kΩ
                        |
                       GND

Encoder B ---- 1 kΩ ----+---- STM32 timer input
                        |
                       15 kΩ
                        |
                       GND

Encoder GND -------- STM32 GND -------- XL4015 OUT-
```

- 15 kΩ load는 A/B 각각 하나씩 필요하다.
- Common GND가 필수다.
- 실제 series resistor는 채널별 1 kΩ으로 확정해 시험했다.
- 1 kΩ 뒤 STM32 input node에서 15 kΩ을 common GND로 연결했다.
- PB4/PB5를 분리한 사전 측정에서 MG540-A의 A/B HIGH는 모두 3.06 V, MG540-B의 A/B HIGH는 3.06~3.07 V였다.
- 첫 timer 입력은 `PB4/TIM3_CH1 = A`, `PB5/TIM3_CH2 = B`로 검증했다.
- 두 번째 timer 입력은 `PA0/TIM5_CH1 = A`, `PA1/TIM5_CH2 = B`로 검증했다.
- 이 단계에서는 motor power를 넣지 않고 shaft를 손으로만 돌린다.

## Test 6: Direction Sign and Count

TIM3는 `TI1 and TI2` encoder mode, x4 counting, prescaler 0, period 65535,
rising/direct input, filter 0, no NVIC로 설정했다. Firmware는 counter를 32768에서
시작하고 USART2/COM3에 250 ms 주기로 임시 bench log를 출력했다.

| Bench motor | Bench timer path | Clockwise 1 rev | Counter-clockwise 1 rev | Provisional counts/output rev | Vehicle side |
| --- | --- | ---: | ---: | ---: | --- |
| MG540-A | TIM3 PB4/PB5 | +1560 | -1560~-1570 | 1560 | TBD |
| MG540-B | TIM3 PB4/PB5 | +1562 | -1560 | 1560 | TBD |

Clockwise/counter-clockwise는 output shaft 끝을 정면으로 바라본 기준이다. 두 motor는
같은 TIM3 bench input에 순차 연결해 시험했으며, 정지 시 count가 고정되고 방향을
바꾸면 증가/감소 방향이 반전됐다. Reset이나 비정상적인 대형 count jump는 관찰되지 않았다.

Evidence:

- [`../assets/logs/encoder/2026-07-26_tim3_mg540a_bidirectional_hand_rotation_raw.txt`](../assets/logs/encoder/2026-07-26_tim3_mg540a_bidirectional_hand_rotation_raw.txt)
- [`../assets/logs/encoder/README.md`](../assets/logs/encoder/README.md)

Raw serial log는 MG540-A에서 정지 count와 양방향 증감만 담은 부분 로그다. 위의
1회전 수치와 MG540-B 결과는 같은 bench session에서 별도로 관찰·보고한 값이며,
raw log 하나가 표 전체를 증명하는 것으로 해석하지 않는다.

### 2026-07-27 TIM3/TIM5 dual-input retest

TIM3는 16-bit counter를 `32768`에서, TIM5는 32-bit counter를 `0x80000000`에서
시작했다. 두 encoder를 동시에 연결하고 한 encoder씩 손으로 회전·복귀시켜
반대쪽 counter가 고정되는지 확인했다.

| Phase | Active path | Raw-log centered count | Inactive path | Result |
| --- | --- | ---: | --- | --- |
| First rotation and return | ENC5 / TIM5 PA0/PA1 | `0 -> +1557 -> -6` | ENC3 remained `0` | PASS |
| Second rotation and return | ENC3 / TIM3 PB4/PB5 | `0 -> +1561 -> +7` | ENC5 remained `-6` | PASS |

사용자가 같은 bench session에서 별도로 보고한 새 경로 출력축 1회전 값은
`+1555 / -1566`이고, 기존 시험 encoder도 이전의 약 1560 count/rev를
재현했다. 이 숫자는 별도 관찰값이며 raw log의 isolated endpoint로 기록된
값은 아니다.

손회전 시험에는 정확한 360° 시작·종료를 고정하는 jig가 없었다. 기준선 정렬,
미세한 초과 회전과 gearbox backlash가 포함될 수 있으므로 이 값은 정확한
encoder CPR calibration이 아니라 `약 1560 counts/output rev`의 기능시험
잠정값이다. 최종 보정은 축 기준선을 표시하고 여러 바퀴의 총 count를 회전수로
나누는 방식으로 반복 측정한다.

Dual evidence:

- [`../assets/logs/encoder/2026-07-27_tim3_tim5_dual_encoder_independent_hand_rotation_raw.txt`](../assets/logs/encoder/2026-07-27_tim3_tim5_dual_encoder_independent_hand_rotation_raw.txt)
- [`../assets/logs/encoder/README.md`](../assets/logs/encoder/README.md)

제한:

- TIM3의 `raw - 32768`과 TIM5의 `raw - 0x80000000`은 제한적인 손회전 표시값이며 production wrap-safe delta/누적 count가 아니다.
- Filter 0과 DMM 측정은 motor-off 조건만 검증한다. Powered motor noise, overshoot와 적절한 input filter는 미검증이다.
- Oscilloscope/logic analyzer로 LOW, pulse width와 A/B phase timing을 계측하지 않았다.
- 실제 vehicle left/right와 forward-positive sign은 미확정이다.

MG540-A/B를 실제 차량 left/right로 부르지 않는다. `left_cps/right_cps`는 현재
firmware의 논리 field 이름이며 vehicle-side 증거가 아니다. 실제 장착 방향과
forward 기준이 정해진 뒤 channel assignment와 sign inversion을 확정한다.

## Test 7: STM32 TEL -> ESP32 End-to-End CPS

Main DC switch를 켜고 motor-output hook을 `0U`로 비활성화해 commanded output을
zero로 유지한 상태에서 motor A를 먼저, motor B를 다음에 손으로 돌렸다. 두 motor는
동시에 돌리지 않았다. Production path는 TIM3/TIM5 -> wrap-safe CPS -> STM32 UART
`TEL` -> ESP32 parser/log다. Motor lead의 물리적 분리 여부는 이 raw log가 증명하지
않으며, active PWM/motor-current가 발생하는 powered-noise 시험과 구분한다.

| Operator sequence | Active TEL field | Direction result | Inactive field | Result |
| --- | --- | --- | --- | --- |
| Motor A clockwise | `right_cps` / TIM5 | 22 moving samples, `+10..+580` | `left_cps=0` | PASS |
| Motor B clockwise | `left_cps` / TIM3 | normal moving samples `+10..+390` | `right_cps=0` | PASS |
| Motor A counter-clockwise | `right_cps` / TIM5 | 30 negative samples, `-560..-10` | `left_cps=0` | PASS |
| Motor B counter-clockwise | `left_cps` / TIM3 | 29 negative samples, `-760..-10` | `right_cps=0` | PASS |

- Clean reset/stationary capture에서 두 CPS field는 0이었다.
- Clockwise capture의 230개 TEL row와 counter-clockwise capture의 165개 TEL row는
  각각 `t_ms +100`, `tel_count +1`로 연속했다.
- Stop transition에서 관찰된 단일 `-10` 또는 `+20` rebound sample은 지속되지
  않았고 이후 0으로 복귀했다.
- 회전 로그의 누적 `err=2`는 scripted sequence의 의도된 `NOT_ARMED`와
  `OUT_OF_RANGE` negative case다. 회전 중 새 parse/frame error는 없었다.

Evidence:

- [`../assets/logs/encoder/2026-07-29_dual_encoder_cps_uart_telemetry_verification.md`](../assets/logs/encoder/2026-07-29_dual_encoder_cps_uart_telemetry_verification.md)
- [`../assets/logs/encoder/2026-07-29_dual_encoder_cps_tel_cw_pass.txt`](../assets/logs/encoder/2026-07-29_dual_encoder_cps_tel_cw_pass.txt)
- [`../assets/logs/encoder/2026-07-29_dual_encoder_cps_tel_ccw_pass.txt`](../assets/logs/encoder/2026-07-29_dual_encoder_cps_tel_ccw_pass.txt)

## Test 8: 50-Revolution Calibration and CPS to mRPM

2026-07-26~27의 1회전 결과는 기능 확인용 잠정 scale이었다. 2026-07-30에는
출력축을 방향별 50회전시키고 총 count를 회전수로 나눴다. 반시계 총 count는
실제 음수였으며 표에서는 절댓값으로 비교한다.

| Bench motor | Direction | Revolutions | Absolute count | Counts/output rev |
| --- | --- | ---: | ---: | ---: |
| MG540-A | Clockwise | 50 | 77,998 | 1559.96 |
| MG540-A | Counter-clockwise | 50 | 78,001 | 1560.02 |
| MG540-B | Clockwise | 50 | 78,000 | 1560.00 |
| MG540-B | Counter-clockwise | 50 | 78,000 | 1560.00 |

따라서 현재 STM32 quadrature x4와 출력축 기준 firmware 상수는
`1560 counts/output rev`로 확정한다. 이 50회전 숫자는 작업자가 별도로 관찰한
측정값이며 아래 dynamic raw log 자체에 들어 있는 endpoint는 아니다.

Firmware는 다음 정수 변환을 사용한다.

```text
mRPM = trunc(CPS * 60000 / 1560)
```

- Boot: `ENC_SELF_TEST,wrap=PASS,millirpm=PASS`
- Dynamic raw log: 305 complete dual row, 610 channel sample, malformed 0
- CPS -> mRPM formula mismatch: 0 / 610
- Direction mismatch: 0
- Simultaneous active dual-channel row: 0
- 마지막 26 row: 양 channel `delta=0`, `cps=0`, `mrpm=0`

Evidence:

- [`../assets/logs/encoder/2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md`](../assets/logs/encoder/2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md)
- [`../assets/logs/encoder/2026-07-30_50rev_output_shaft_calibration_operator_record.txt`](../assets/logs/encoder/2026-07-30_50rev_output_shaft_calibration_operator_record.txt) (`OPERATOR_REPORTED_BENCH_OBSERVATION`, raw serial 아님)
- [`../assets/logs/encoder/2026-07-30_dual_encoder_millirpm_hand_rotation_pass.txt`](../assets/logs/encoder/2026-07-30_dual_encoder_millirpm_hand_rotation_pass.txt)

이 PASS는 external tachometer 기반 절대 RPM 정확도, wheel 이동거리, vehicle
left/right·forward sign 또는 powered-motor noise를 포함하지 않는다. mRPM은 현재
USART2 bench diagnostic field이며 production `TEL`은 signed CPS 계약을 유지한다.

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
| 1 kΩ series + 15 kΩ pull-down HIGH | `PASS FOR MOTOR-OFF HAND TEST` | MG540-A/B A/B 3.06~3.07 V |
| Output structure | `PROBABLE` | 약 10 kΩ internal 5 V pull-up과 일치하지만 회로형식 미확정 |
| Quadrature behavior | `FUNCTIONALLY OBSERVED` | TIM3 x4 count와 direction reversal PASS; scope phase timing 미계측 |
| STM32 input protection | `BENCH-CONFIRMED / POWERED-NOISE TBD` | 채널별 1 kΩ series + 15 kΩ pull-down, common GND |
| Direction sign and count | `PASS ON TIM3/TIM5 (MOTOR-OFF)` | Sequential TIM3 result와 dual independent hand rotation |
| Counts per output revolution | `PASS` | 방향별 50회전 손보정 `1559.96~1560.02`; firmware 상수 1560 counts/output rev |
| Dual input independence | `PASS` | TIM5 active 동안 TIM3 fixed, TIM3 active 동안 TIM5 fixed |
| Limited hand-rotation STM32 test | `PASS` | Motor power disconnected, both encoders concurrently connected |
| Production TEL CPS | `PASS` | Both signed CPS fields reached ESP32 at 100 ms TEL interval |
| ESP32 structured CPS parse | `PASS` | Independent CW/CCW sign, inactive-channel zero와 stop-to-zero 확인 |
| CPS to mRPM calculation | `PASS` | wrap/millirpm self-test와 610 sample formula/sign 일치, stop-to-zero |
| Powered closed-loop operation | `NOT READY` | Motor-on noise, active motor safety와 no-load 시험 필요 |

## Next Step

1. 현재 TIM3/TIM5 firmware, production TEL/ESP32 parser, 50회전 상수와 dated raw evidence를 Git 기준점으로 보존한다.
2. Vehicle left/right assignment와 forward-positive sign을 실제 장착 뒤 확정한다.
3. External tachometer 기준 절대 RPM 정확도와 sprocket/track 이동거리로 wheel-speed 변환값을 검증한다.
4. Powered motor noise와 input filter는 계측 장비 또는 제한된 lifted test에서 별도 검증한다.
5. Powered/no-motor timeout/DISARM LED functional gate는 통과했다. 실제 motor no-load 시험은 actual PB6/PB7 shutdown waveform, direction timing과 fault/E-stop gate까지 통과한 뒤 진행한다.

관련 절차: [`05_First_Motor_No_Load_Test.md`](05_First_Motor_No_Load_Test.md)

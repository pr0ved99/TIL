# 002 TIM Encoder Mode Bring-Up

## Status

Partial — TIM3/TIM5 dual motor-power-off independent hand-rotation PASS; production speed와 powered-noise pending

## Purpose

MG540-A/B encoder A/B 신호를 STM32 timer encoder mode로 읽고, motor power 없이
정지 count 안정성, 회전 방향별 signed count와 provisional 1회전 count를 확인한다.

## Hardware

| Function | Assignment / state |
| --- | --- |
| TIM3 encoder A/B | `PB4/TIM3_CH1 = A`, `PB5/TIM3_CH2 = B`; motor-power-off PASS |
| TIM3 mode | `TIM_ENCODERMODE_TI12`, x4 quadrature count |
| TIM5 encoder A/B | `PA0/TIM5_CH1 = A`, `PA1/TIM5_CH2 = B`; motor-power-off PASS |
| Per-channel conditioning | Encoder signal -> 1 kΩ series -> MCU node; MCU node -> 15 kΩ -> common GND |

## Pre-Checks

- encoder output과 최종 MCU-side conditioned voltage를 먼저 확인한다.
- Raw encoder signal은 직접 연결하지 않고 A/B마다 확정된 1 kΩ/15 kΩ network를 유지한다.
- encoder GND와 STM32 GND를 공통으로 둔다.
- 모터 전원 없이 손으로 돌려 count 변화부터 확인한다.

## Learning Points

- Timer encoder mode에서 CH1/CH2가 A/B 입력으로 쓰이는 구조
- counter 증가/감소 방향
- 16-bit timer wraparound 처리
- count delta로 counts/s 계산
- forward command와 encoder sign mapping

## Completed TIM3 Test

1. TIM3 TI12 encoder mode를 PB4/PB5에 설정했다.
2. MG540-A와 MG540-B를 같은 TIM3 입력에 한 대씩 순차 연결했다.
3. Motor power를 분리하고 output shaft를 손으로 돌렸다.
4. 정지 중 count가 안정적인지와 양방향 count 증감을 확인했다.
5. Output shaft end를 정면에서 본 CW/CCW 기준으로 1회전 count를 기록했다.

| Bench motor | Stationary | CW | CCW | Provisional counts/output rev |
| --- | --- | ---: | ---: | ---: |
| MG540-A | Stable during observation | 약 +1560 | 약 -(1560~1570) | 약 1560 |
| MG540-B | Stable during observation | +1562 | -1560 | 약 1560 |

CW에서 positive, CCW에서 negative였지만 이는 TIM3 bench wiring과 shaft-end-view
기준이다. 차량 left/right와 forward sign은 아직 확정하지 않는다.

## Evidence

- Raw log: [`../../assets/logs/encoder/2026-07-26_tim3_mg540a_bidirectional_hand_rotation_raw.txt`](../../assets/logs/encoder/2026-07-26_tim3_mg540a_bidirectional_hand_rotation_raw.txt)
- Evidence index and result boundary: [`../../assets/logs/encoder/README.md`](../../assets/logs/encoder/README.md)
- Encoder voltage and conditioning: [`../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md`](../../02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md)

Raw serial log는 MG540-A의 정지 안정성과 방향별 증감만 직접 보여 준다. 정확한
1-output-revolution 값과 MG540-B 결과는 같은 bench session에서 별도로 보고된
측정이므로 provisional로 유지한다.

손으로 정확히 360°의 시작점과 종료점을 맞추는 데는 한계가 있고 gearbox
backlash도 포함될 수 있다. 따라서 한 바퀴 결과는 기능 확인용 잠정값이며,
최종 counts/rev는 축에 기준선을 표시해 여러 바퀴를 반복 측정한 뒤 총 count를
회전수로 나누어 보정한다.

## Follow-Up

- TIM5 PA0/PA1의 motor-power-off 시험과 TIM3/TIM5 dual 독립 count는 2026-07-27에 통과했다.
- 다음은 16-bit/32-bit wrap-safe delta와 speed telemetry를 구현한다.
- Powered motor 상태에서 noise, false count와 reset 여부를 확인한다.
- 차량 장착 후 left/right와 forward sign을 확정한다.
- MDD10A no-load motor test와 연결한다.
- UART telemetry로 `left_count`, `right_count`, `left_cps`, `right_cps`를 송신한다.
- encoder-only odometry 계산으로 확장한다.

# 002 TIM Encoder Mode Bring-Up

## Status

Planned

## Purpose

좌우 모터 encoder A/B 신호를 STM32 timer encoder mode로 읽을 수 있는지 확인한다.

## Hardware

| Function | Candidate |
| --- | --- |
| Left encoder A/B | PB4 / PB5, TIM3_CH1 / TIM3_CH2 |
| Right encoder A/B | PA0 / PA1, TIM5_CH1 / TIM5_CH2 |

## Pre-Checks

- encoder output voltage를 DMM 또는 oscilloscope로 먼저 확인한다.
- STM32 input limit을 넘는 신호는 직접 연결하지 않는다.
- encoder GND와 STM32 GND를 공통으로 둔다.
- 모터 전원 없이 손으로 돌려 count 변화부터 확인한다.

## Learning Points

- Timer encoder mode에서 CH1/CH2가 A/B 입력으로 쓰이는 구조
- counter 증가/감소 방향
- 16-bit timer wraparound 처리
- count delta로 counts/s 계산
- forward command와 encoder sign mapping

## Minimal Test

1. TIM3 encoder mode를 PB4/PB5에 설정한다.
2. TIM5 encoder mode를 PA0/PA1에 설정한다.
3. timer를 start한다.
4. 손으로 모터를 천천히 돌리며 `TIMx->CNT` 변화를 확인한다.
5. A/B를 바꾸거나 sign convention을 수정해야 하는지 기록한다.

## Evidence To Capture

- 손 회전 시 count 증가/감소 log
- forward/reverse 방향별 sign table
- encoder voltage 측정값
- count delta와 sample time 기반 speed 계산 예시

## Follow-Up

- MDD10A no-load motor test와 연결한다.
- UART telemetry로 `left_count`, `right_count`, `left_cps`, `right_cps`를 송신한다.
- encoder-only odometry 계산으로 확장한다.

# PWM, Encoder, PID, Calibration

## 분야

- 모터 제어
- 임베디드 제어
- 로봇 구동부 보정

## 관련 면접 질문

- DC 모터를 어떻게 제어했는가?
- PWM과 direction은 무엇인가?
- 누적 오차와 calibration 문제를 어떻게 보정했는가?
- encoder feedback을 사용하면 무엇이 좋은가?

## 선수지식

- 전압과 duty cycle
- DC 모터
- 속도와 위치
- encoder tick
- feedback control

## PWM

PWM은 Pulse Width Modulation의 약자입니다. 일정한 주기 안에서 high인 시간의 비율, 즉 duty cycle을 조절해 평균 전압처럼 사용합니다.

```text
Duty 20%: 낮은 출력
Duty 80%: 높은 출력
```

DC 모터 제어에서는 보통 PWM으로 속도 크기를 조절하고, direction pin으로 회전 방향을 결정합니다.

```text
PWM: 속도 크기
DIR: 방향
```

## Open-loop 제어

PWM duty를 주고 "이 정도면 이 속도로 돌겠지"라고 가정하는 방식은 open-loop 제어입니다.

장점:

- 구현이 쉽습니다.
- 초기 동작 검증에 적합합니다.

단점:

- 배터리 전압, 바닥 마찰, 모터 편차에 따라 실제 속도가 달라집니다.
- 좌우 모터가 같은 PWM을 받아도 같은 속도로 돌지 않을 수 있습니다.
- 누적 오차가 생깁니다.

## Encoder

Encoder는 모터나 바퀴가 얼마나 회전했는지 tick으로 알려주는 센서입니다.

Encoder를 사용하면 실제 속도나 이동 거리를 계산할 수 있습니다.

```text
wheel_rotation = encoder_tick / ticks_per_revolution
distance = wheel_rotation * 2 * pi * wheel_radius
```

## Closed-loop 제어

Closed-loop 제어는 목표값과 실제값의 차이를 보고 보정하는 방식입니다.

```text
error = target_speed - measured_speed
```

이 error를 줄이도록 PWM을 조절합니다.

## PID 제어

PID는 error를 기반으로 제어 입력을 계산하는 대표적인 방법입니다.

- P: 현재 오차에 비례해 보정
- I: 누적 오차를 줄임
- D: 오차 변화율을 보고 급격한 변화를 완화

모터 속도 제어에서는 PI 제어만으로도 충분한 경우가 많습니다.

## Calibration

Calibration은 실제 하드웨어 편차를 측정해 보정하는 과정입니다.

예:

- 왼쪽 모터가 오른쪽보다 5% 느리면 왼쪽 PWM을 조금 더 줌
- wheel radius 실제값을 측정해 거리 계산에 반영
- encoder tick per revolution을 확인
- deadband를 측정해 모터가 실제로 돌기 시작하는 최소 PWM을 찾음

## 면접 답변으로 연결

### 30초 답변

> 초기 검증에서는 PWM duty와 direction으로 모터 회전 방향과 속도 변화를 확인할 수 있습니다. 하지만 정밀 제어를 위해서는 encoder tick으로 실제 바퀴 속도나 이동 거리를 측정하고, 목표 속도와 실제 속도의 차이를 PI/PID 제어로 보정해야 합니다. 또한 wheel radius, gear ratio, motor별 편차, deadband를 측정해 calibration coefficient를 적용하면 누적 오차를 줄일 수 있습니다.

## 내 프로젝트로 연결하는 문장

> 제 프로젝트에서는 PWM/direction 기반으로 동작 검증을 했고, 개선한다면 encoder feedback을 추가해 목표 속도와 실제 속도의 차이를 계산하고 wheel별 보정 계수를 적용하겠다고 답하는 것이 적절합니다.


# R05 Motor Control Task Skeleton

## 목표

Tracked mobile robot 하부제어 firmware의 첫 task skeleton을 만든다.

## 최소 task

```text
motor_control_task  100 Hz
safety_task         50-100 Hz
comm_task           event-driven or 100 Hz
telemetry_task      10 Hz
battery_task        10 Hz
```

## command flow

```text
comm_task
-> command_queue
-> motor_control_task
-> safety gate
-> PWM output
```

## 안전 규칙

- `comm_task`는 PWM을 직접 쓰지 않는다.
- `telemetry_task`는 motor timing을 방해하지 않는다.
- `safety_task`는 command source와 독립적으로 motor output을 막을 수 있다.
- command timeout은 항상 동작해야 한다.

## 완료 기준

- 각 task가 주기 counter를 증가시킨다.
- telemetry에서 각 task alive counter를 볼 수 있다.
- command timeout 시 motor output request가 0으로 바뀐다.
- safety disallow 상태에서 PWM이 0으로 유지된다.
